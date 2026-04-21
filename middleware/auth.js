const jwt = require('jsonwebtoken');

const JWT_SECRET = process.env.JWT_SECRET || 'itinerate-dev-secret-change-in-production';

function requireAuth(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing or malformed Authorization header.' });
  }

  const token = authHeader.slice(7);
  try {
    const payload = jwt.verify(token, JWT_SECRET);
    req.user = payload;
    next();
  } catch (err) {
    if (err.name === 'TokenExpiredError') {
      return res.status(401).json({ error: 'Session expired. Please log in again.' });
    }
    return res.status(401).json({ error: 'Invalid token.' });
  }
}

function requireAdmin(req, res, next) {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Missing or malformed Authorization header.' });
  }

  const token = authHeader.slice(7);
  try {
    const payload = jwt.verify(token, JWT_SECRET);
    // Re-check admin status live from DB so revocations take effect immediately
    const { getDB } = require('../db');
    const db = getDB();
    const user = db.prepare('SELECT id, is_admin FROM users WHERE id = ?').get(payload.id);
    if (!user || !user.is_admin) {
      return res.status(403).json({ error: 'Admin access required.' });
    }
    req.user = { ...payload, is_admin: user.is_admin };
    next();
  } catch (err) {
    if (err.name === 'TokenExpiredError') {
      return res.status(401).json({ error: 'Session expired. Please log in again.' });
    }
    return res.status(401).json({ error: 'Invalid token.' });
  }
}

module.exports = { requireAuth, requireAdmin, JWT_SECRET };
