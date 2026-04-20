#!/usr/bin/env python
import sys
from chromadb_document_processor.flights_crew import FlightsCrew


def run():
    inputs = {"query": "fly from JFK to LAX on 2026-05-01"}
    FlightsCrew().crew().kickoff(inputs=inputs)


def run_with_trigger(**kwargs):
    inputs = kwargs if kwargs else {"query": "fly from JFK to LAX on 2026-05-01"}
    FlightsCrew().crew().kickoff(inputs=inputs)


def train():
    inputs = {"query": "fly from JFK to LAX on 2026-05-01"}
    try:
        FlightsCrew().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    try:
        FlightsCrew().crew().replay(task_id=sys.argv[1])
    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    inputs = {"query": "fly from JFK to LAX on 2026-05-01"}
    try:
        FlightsCrew().crew().test(n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: main.py <command> [<args>]")
        sys.exit(1)

    command = sys.argv[1]
    if command == "run":
        run()
    elif command == "train":
        train()
    elif command == "replay":
        replay()
    elif command == "test":
        test()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
