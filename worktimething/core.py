import os
import time
import click
import json
from contextlib import contextmanager

# n seconds
M = 60
H = 60 * M
D = 24 * H
W = 7 * D


@contextmanager
def jsondb(path):
    """
    Edit a given dictionary and it will be persisted on exit.
    """
    d = {"timeline": []}
    if os.path.exists(path):
        with open(path, "r") as fl:
            d = json.loads(fl.read())
    yield d
    with open(path, "w") as fl:
        fl.write(json.dumps(d, indent=2))


def to_jira(total):
    "Turn total seconds to a jira work entry timestamp"
    m, h, d, w = [int(i) for i in [M, H, D, W]]
    w, total = int(total // w), total % w
    d, total = int(total // d), total % d
    h, total = int(total // h), total % h
    m, total = int(total // m), total % m
    val = ""
    if w:
        val += f"{w}w"
    if d:
        val += f" {d}d"
    if h:
        val += f" {h}h"
    if m:
        val += f" {m}m"
    return val.strip()


def read_jira(s):
    seconds = 0
    magnitude = ""
    for i in s:
        if i.isdigit():
            magnitude += i
        elif i.isspace():
            continue
        else:
            unit = {"w": W, "d": D, "h": H, "m": M}[i]
            seconds += int(magnitude) * unit
            magnitude = ""
    return seconds


@click.command(name="python -m worktimething")
@click.argument("cmd", default="summary")
@click.argument("slug", default="")
@click.argument("diff", default="")
@click.option("--json-path", default="db.json", help="Where to store data?")
def run(cmd, slug, diff, json_path):
    def add():
        "Manually add a time entry"
        assert cmd and slug and diff
        seconds = read_jira(diff)
        with jsondb(json_path) as db:
            db["timeline"].append((seconds, slug, "adjust"))

    def sub():
        "Manually subtract a time entry"
        add()
        with jsondb(json_path) as db:
            db["timeline"][-1][0] *= -1

    def begin():
        """
        Begin recording time on some slug. Automatically stops time if it was
        being recorded for a previous task
        """
        assert cmd and slug
        with jsondb(json_path) as db:
            if db["timeline"]:
                last_time, last_slug, last_act = db["timeline"][-1]
                if last_slug != slug and last_act == "begin":
                    db["timeline"].append((time.time(), last_slug, "end"))
                if last_slug == slug and last_act == "begin":
                    print("This task is currently running")
                    return
            db["timeline"].append((time.time(), slug, "begin"))

    def end():
        """
        Stop recording time for some slug.
        """
        assert cmd and slug
        with jsondb(json_path) as db:
            if db["timeline"]:
                last_time, last_slug, last_act = db["timeline"][-1]
                assert last_slug == slug and last_act == "begin"
            db["timeline"].append((time.time(), slug, "end"))

    def summary():
        """
        Show a summary of time spent so far.
        """
        with jsondb(json_path) as db:
            last_slug = None
            started_at = None
            totals = {
                slug: {"total": 0, "started_at": None, "running": False, "adjust": 0}
                for _, slug, _ in db["timeline"]
            }
            total_time = 0
            for slug, data in totals.items():
                for stamp, _, act in (x for x in db["timeline"] if x[1] == slug):
                    if act == "begin":
                        data["started_at"] = stamp
                        data["running"] = True
                    elif act == "end":
                        data["total"] += stamp - data["started_at"]
                        data["started_at"] = None
                        data["running"] = False
                    elif act == "adjust":
                        data["adjust"] += stamp
                prefix = "*" if data["running"] else " "
                total = (
                    data["total"] + (time.time() - data["started_at"])
                    if data["running"]
                    else data["total"]
                )
                total += data["adjust"]
                total_time += total

                print(f"{slug:>5} : {prefix} {to_jira(total)}")
            print("-" * 20)
            print(f"{'TOTAL':>5} :   {to_jira(total_time)}")

    # cmd aliases
    b = start = begin
    e = stop = end
    a = add
    s = sub
    if cmd not in locals():
        print("Commands can only be one of:")
        print(
            """
        b = start = begin
        e = stop = end
        a = add
        s = sub
        """
        )
    else:
        exec(f"{cmd}()")
    if cmd != "summary":
        print(summary())
