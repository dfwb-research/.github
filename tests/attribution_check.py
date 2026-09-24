"""Run a workflow's attribution step against throwaway git histories.

Usage: python tests/attribution_check.py <workflow.yml> <job>
A clean history must pass (exit 0); a history with a Co-Authored-By or "Generated with" trailer
must fail (exit 1).
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

STEP_PREFIX = "Reject AI/bot attribution"


def attribution_script(workflow: str, job: str) -> str:
    steps = yaml.safe_load(Path(workflow).read_text())["jobs"][job]["steps"]
    return next(s["run"] for s in steps if s.get("name", "").startswith(STEP_PREFIX))


def repo_with(messages: list[str]) -> str:
    path = tempfile.mkdtemp()
    subprocess.run(["git", "init", "-q", path], check=True)
    identity = ["-c", "user.name=t", "-c", "user.email=t@example.org"]
    for message in messages:
        commit = ["commit", "-q", "--allow-empty", "-m", message]
        subprocess.run(["git", "-C", path, *identity, *commit], check=True)
    return path


def run(script: str, path: str, before: str = "0" * 40) -> int:
    head = subprocess.run(
        ["git", "-C", path, "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    env = {
        **os.environ,
        "EVENT_NAME": "push",
        "PR_BASE": "",
        "PR_HEAD": "",
        "PUSH_BEFORE": before,  # all zeros: a new branch, so the step checks the whole history
        "HEAD_SHA": head,
    }
    done = subprocess.run(["bash", "-c", script], cwd=path, env=env, check=False)
    return done.returncode


def main() -> None:
    script = attribution_script(sys.argv[1], sys.argv[2])
    # The clean history also proves that an ordinary "generated with" sentence is not flagged.
    clean = repo_with(["feat: add a thing", "fix: a bug\n\nFixtures generated with seed 0."])
    co_authored = repo_with(["feat: add a thing", "fix: x\n\nCo-Authored-By: A <a@example.org>"])
    generated = repo_with(["docs: readme\n\nGenerated with Claude"])
    unknown_base = "1234567890abcdef1234567890abcdef12345678"  # e.g. the old tip after a force-push
    results = (
        run(script, clean),
        run(script, co_authored),
        run(script, generated),
        run(script, co_authored, before=unknown_base),
    )
    print("clean, co-authored, generated-with, unknown-base ->", results)
    if results != (0, 1, 1, 1):
        raise SystemExit(f"unexpected results {results}")
    print("attribution check OK")


if __name__ == "__main__":
    main()
