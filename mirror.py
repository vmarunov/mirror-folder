__author__ = 'Vladimir'

import argparse

parser = argparse.ArgumentParser(description='Mirroring folder', add_help=True)
parser.add_argument('source', nargs=1,  help='Source folder')
parser.add_argument('destination', nargs=1,  help='Destination folder')
parser.add_argument('--test', dest='test', action='store_true', help='Only test')
args = parser.parse_args()

print args.source
print args.destination
