import argparse
from . import core

parser = argparse.ArgumentParser()
parser.add_argument("-f", default="summary")  # fn
parser.add_argument("-s", default=None)  # slug
parser.add_argument("--json_path", default="db.json")
args = parser.parse_args()

core.run(args)
