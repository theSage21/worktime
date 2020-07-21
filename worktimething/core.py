import os
import time
import click
import json
from contextlib import contextmanager


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
        fl.write(json.dumps(d))


def to_jira(total):
    "Turn total seconds to a jira work entry timestamp"
    m = 60
    h = 60 * m
    d = 24 * h
    w = 7 * d
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


@click.command(name="python -m worktimething")
@click.argument("cmd", default="summary")
@click.argument("slug", default="")
@click.option("--json-path", default="db.json", help="Where to store data?")
def run(cmd, slug, json_path):
    if cmd != "summary":
        assert slug is not None

    def begin():
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
        with jsondb(json_path) as db:
            if db["timeline"]:
                last_time, last_slug, last_act = db["timeline"][-1]
                assert last_slug == slug and last_act == "begin"
            db["timeline"].append((time.time(), slug, "end"))

    def summary():
        with jsondb(json_path) as db:
            last_slug = None
            started_at = None
            totals = {
                slug: {"total": 0, "started_at": None, "running": False}
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
                prefix = "*" if data["running"] else " "
                total = (
                    data["total"] + (time.time() - data["started_at"])
                    if data["running"]
                    else data["total"]
                )
                total_time += total

                print(f"{slug:>5} : {prefix} {to_jira(total)}")
            print("-" * 20)
            print(f"{'TOTAL':>5} :   {to_jira(total_time)}")

    b = start = begin
    e = stop = end
    exec(f"{cmd}()")
    if cmd != "summary":
        print(summary())
