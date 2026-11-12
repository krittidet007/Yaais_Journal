#!/usr/bin/env python3
"""Check every stop's puzzle: the prepared solution must pass, the pre-filled
starter code must fail.

    python tools/check_validator.py

Exits non-zero if any stop breaks that rule, so it can be used in CI.
"""
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

pygame.init()
from game import story as ST, tablets as TB  # noqa: E402
from tests.test_tablets import SOLUTIONS  # noqa: E402


def main():
    print("VALIDATOR CHECK - every stop, solution and prefill")
    print("-" * 62)
    accepted = rejected = bad = 0
    for stop in ST.STOPS:
        spec = ST.code_of(stop["id"])
        if spec is None:
            print("%-14s no puzzle" % stop["id"])
            continue
        ok_solution, _, _ = TB.validate(spec, SOLUTIONS[stop["id"]])
        ok_prefill, _, _ = TB.validate(spec, spec["prefill"])
        accepted += bool(ok_solution)
        rejected += bool(not ok_prefill)
        bad += not (ok_solution and not ok_prefill)
        print("%-14s solution %-9s prefill %s" % (
            stop["id"],
            "ACCEPTED" if ok_solution else "REJECTED",
            "REJECTED" if not ok_prefill else "ACCEPTED"))
    print("-" * 62)
    print("RESULT: %d/24 solutions accepted | %d/24 prefills rejected | mismatches: %d"
          % (accepted, rejected, bad))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
