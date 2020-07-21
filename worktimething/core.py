import os
import time
import json
from contextlib import contextmanager


@contextmanager
def jsondb(path):
    d = {"timeline": [], "summary": {}}
    if os.path.exists(path):
        with open(path, "r") as fl:
            d = json.loads(fl.read())
    yield d
    with open(path, "w") as fl:
        fl.write(json.dumps(d))


def to_jira(total):
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


def run(args):
    if args.f != "summary":
        assert args.s is not None

    def begin():
        with jsondb(args.json_path) as db:
            last_time, last_slug, last_act = db["timeline"][-1]
            if last_slug != args.s and last_act == "begin":
                db["timeline"].append((time.time(), last_slug, "end"))
            db["timeline"].append((time.time(), args.s, "begin"))

    def end():
        with jsondb(args.json_path) as db:
            last_time, last_slug, last_act = db["timeline"][-1]
            assert last_slug == args.s and last_act == "begin"
            db["timeline"].append((time.time(), args.s, "end"))

    def summary():
        with jsondb(args.json_path) as db:
            last_slug = None
            started_at = None
            totals = {
                slug: {"total": 0, "started_at": None, "running": False}
                for _, slug, _ in db["timeline"]
            }
            for slug, data in totals.items():
                for stamp, _, act in (x for x in db["timeline"] if x[1] == slug):
                    if act == "begin":
                        data["started_at"] = stamp
                        data["running"] = True
                    elif act == "end":
                        data["total"] += time.time() - data["started_at"]
                        data["started_at"] = None
                        data["running"] = False
                prefix = "*" if data["running"] else " "
                total = (
                    data["total"] + (time.time() - data["started_at"])
                    if data["running"]
                    else data["total"]
                )

                print(f"{slug:>20} : {prefix} {to_jira(total)}")

    b = begin
    e = end
    exec(f"{args.f}()")
    if args.f != "summary":
        print(summary())
