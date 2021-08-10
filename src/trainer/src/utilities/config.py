import argparse
import json

def get_config(filename=None):
  if filename is None:
    parser = argparse.ArgumentParser(
        description="Get input JSON file as input")
    parser.add_argument('inputFile',
                        help='The input JSON file to drive the simulation')
    args = parser.parse_args()
    filename = args.inputFile

  with open(filename, "r") as fd:
    config = json.load(fd)
  
  return config
