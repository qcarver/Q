from __future__ import annotations

import argparse
from pathlib import Path

from .build import build


parser = argparse.ArgumentParser(description="Build the Überproject-Q launchpad")
parser.add_argument("--target", choices=("local", "lan", "public"), default="local")
args = parser.parse_args()
output = build(Path.cwd(), args.target)
print(output)
