import argparse
import os
from src.external_query import post_result_cache
from src.MKO import MKO
import time

def parse_args():
    parser = argparse.ArgumentParser(description="Trains an MKO")
    parser.add_argument('json_file', metavar='json_file', type=str, help="path to json file for MKO")
    parser.add_argument('username', metavar='username', type=str, help='username of user')
    parser.add_argument('claim_check', metavar='claim_check', type=str, help='claim_check to store in result_cache')
    parser.add_argument('URI', metavar='rc_URI', type=str, help="URI of the result cache")
    return parser.parse_args()

def train_and_post(json_contents, args):
    prev_time = time.time()
    mko = MKO.from_json(json_contents)
    mko.compile()
    mko.train()
    mko_json = mko.get_json()
    generation_time = time.time() - prev_time

    post_result_cache(args.URI, args.username, args.claim_check, generation_time, mko_json)

def main():
    args = parse_args()
    if not os.path.exists(args.json_file):
        raise FileNotFoundError("file '{}' not found".format(args.json_file))

    with open(args.json_file, "r") as file:
        json_contents = file.read()

    train_and_post(json_contents, args)
    

if __name__ == "__main__":
    main()