import sys
from pyramid.paster import bootstrap, setup_logging
from argparse import ArgumentParser

def main():
    parser = ArgumentParser()
    parser.add_argument('--config', metavar='config', type=str, required=True)
    parser.add_argument('--dry-run', action='store_true', default=False)
    opts = parser.parse_args()

    setup_logging(opts.config)
    env = bootstrap(opts.config)

    sys.stdout.write("done\n")
    sys.stdout.flush()
