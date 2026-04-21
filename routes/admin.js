const express = require('express');
const bcrypt = require('bcryptjs');
const { getDB } = require('../db');
const { requireAdmin } = require('../middleware/auth');

const router = express.Router();

// ── GET /api/admin/setup/status  (public — no auth) ──────────────────────────
router.get('/setup/status', (req, res) => {
  const db = getDB();
  const admin = db.prepare('SELECT id FROM users WHERE is_admin = 1 LIMIT 1').get();
  res.json({ needsSetup: !admin });
});

// ── POST /api/admin/setup  (public — creates first admin, then locks) ─────────
router.post('/setup', async (req, res) => {
  const db = getDB();
  const existing = db.prepare('SELECT id FROM users WHERE is_admin = 1 LIMIT 1').get();
  if (existing) {
    return res.status(409).json({ error: 'An admin account already exists.' });
  }

  const { firstName, lastName = '', email, password } = req.body;
  if (!firstName || !email || !password) {
    return res.status(400).json({ error: 'firstName, email, and password are required.' });
  }
  if (password.length < 8) {
    return res.status(400).json({ error: 'Password must be at least 8 characters.' });
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return res.status(400).json({ error: 'Invalid email address.' });
  }

  const dupe = db.prepare('SELECT id FROM users WHERE email = ?').get(email.toLowerCase().trim());
  if (dupe) {
    // Promote the existing account to admin instead of creating a duplicate
    db.prepare('UPDATE users SET is_admin = 1 WHERE id = ?').run(dupe.id);
    return res.json({ message: 'Existing account promoted to admin.' });
  }

  try {
    const hash = await bcrypt.hash(password, 12);
    db.prepare(`
      INSERT INTO users (first_name, last_name, email, password_hash, is_admin)
      VALUES (?, ?, ?, ?, 1)
    `).run(firstName.trim(), lastName.trim(), email.toLowerCase().trim(), hash);
    res.status(201).json({ message: 'Admin account created.' });
  } catch (err) {
    console.error('Setup error:', err);
    res.status(500).json({ error: 'Server error during setup.' });
  }
});

// ── All routes below require admin auth ──────────────────────────────────────
router.use(requireAdmin);

// ── GET /api/admin/stats ──────────────────────────────────────────────────────
router.get('/stats', (req, res) => {
  const db = getDB();
  const totalUsers        = db.prepare('SELECT COUNT(*) as count FROM users').get().count;
  const totalItineraries  = db.prepare('SELECT COUNT(*) as count FROM itineraries').get().count;
  const totalAdmins       = db.prepare('SELECT COUNT(*) as count FROM users WHERE is_admin = 1').get().count;
  const recentUsers       = db.prepare(
    `SELECT COUNT(*) as count FROM users WHERE created_at >= datetime('now', '-7 days')`
  ).get().count;
  res.json({ totalUsers, totalItineraries, totalAdmins, recentUsers });
});

// ── GET /api/admin/users ──────────────────────────────────────────────────────
router.get('/users', (req, res) => {
  const db = getDB();
  const users = db.prepare(
    'SELECT id, first_name, last_name, email, is_admin, created_at FROM users ORDER BY created_at DESC'
  ).all();
  res.json({ users });
});

// ── DELETE /api/admin/users/:id ───────────────────────────────────────────────
router.delete('/users/:id', (req, res) => {
  const targetId = Number(req.params.id);
  if (targetId === req.user.id) {
    return res.status(400).json({ error: 'You cannot delete your own account.' });
  }
  const db = getDB();
  const user = db.prepare('SELECT id FROM users WHERE id = ?').get(targetId);
  if (!user) return res.status(404).json({ error: 'User not found.' });
  db.prepare('DELETE FROM users WHERE id = ?').run(targetId);
  res.json({ message: 'User deleted.' });
});

// ── PUT /api/admin/users/:id/admin ────────────────────────────────────────────
router.put('/users/:id/admin', (req, res) => {
  const targetId = Number(req.params.id);
  if (targetId === req.user.id) {
    return res.status(400).json({ error: 'You cannot change your own admin status.' });
  }
  const db = getDB();
  const user = db.prepare('SELECT id, is_admin FROM users WHERE id = ?').get(targetId);
  if (!user) return res.status(404).json({ error: 'User not found.' });
  const newStatus = user.is_admin === 1 ? 0 : 1;
  db.prepare('UPDATE users SET is_admin = ? WHERE id = ?').run(newStatus, targetId);
  res.json({
    message: newStatus === 1 ? 'User promoted to admin.' : 'Admin rights removed.',
    is_admin: newStatus
  });
});

// ── GET /api/admin/itineraries ────────────────────────────────────────────────
router.get('/itineraries', (req, res) => {
  const db = getDB();
  const itineraries = db.prepare(`
    SELECT i.id, i.user_id, i.destination_id, i.destination_name, i.personality_type,
           i.departure_date, i.return_date, i.saved_at, i.updated_at,
           u.first_name, u.last_name, u.email
    FROM itineraries i
    JOIN users u ON u.id = i.user_id
    ORDER BY i.saved_at DESC
  `).all();
  res.json({ itineraries });
});

// ── DELETE /api/admin/itineraries/:id ────────────────────────────────────────
router.delete('/itineraries/:id', (req, res) => {
  const db = getDB();
  const row = db.prepare('SELECT id FROM itineraries WHERE id = ?').get(Number(req.params.id));
  if (!row) return res.status(404).json({ error: 'Itinerary not found.' });
  db.prepare('DELETE FROM itineraries WHERE id = ?').run(Number(req.params.id));
  res.json({ message: 'Itinerary deleted.' });
});

module.exports = router;
