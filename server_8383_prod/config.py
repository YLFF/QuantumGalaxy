import argparse

parser = argparse.ArgumentParser()
parser.add_argument(
        "--debug",
        type=bool,
        default=False,
        help="debug config",
)

args = parser.parse_args()

