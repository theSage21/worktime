import argparse
from . import core

parser = argparse.ArgumentParser()
parser.add_argument("-f", default="summary", help="Function")  # fn
parser.add_argument("-s", default=None, help="Slug")  # slug
parser.add_argument("--json_path", default="db.json")
args = parser.parse_args()

core.run(args)
