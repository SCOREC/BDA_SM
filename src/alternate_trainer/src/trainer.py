import argparse
import os
from src.external_query import post_result_cache
from src.MKO import MKO
from src.exceptions import InputException, InvalidArgument
from tempfile import NamedTemporaryFile as TempFile
import time

class AddTypes:
    DATA = "data"
    HYPER_PARAMS = "hyper_params"
    HYPER_PARAMS_ABBREV = "hparams"
    TOPOLOGY = "topology"
    types = {
        DATA,
        HYPER_PARAMS,
        HYPER_PARAMS_ABBREV,
        TOPOLOGY
    }

def parse_args():
    parser = argparse.ArgumentParser(description='Trains an MKO')
    parser.add_argument('-f', nargs=1, dest='json_file', const=None, default=None, type=str, help='path to json file for MKO')
    parser.add_argument('--create', dest='function', action='store_const', const='create', default='create', help='create MKO')
    parser.add_argument('--name', nargs=1, dest='name', default='model', help='name of model')
    parser.add_argument('--add', nargs=2, dest='add', help='add to MKO file, first args is type second is location')
    parser.add_argument('--train', dest='function', action='store_const', const='train', help='train MKO object')
    parser.add_argument('username', metavar='username', type=str, help='username of user')
    parser.add_argument('claim_check', metavar='claim_check', type=str, help='claim_check to store in result_cache')
    parser.add_argument('URI', metavar='rc_URI', type=str, help='URI of the result cache')
    return parser.parse_args()


def post(post_args: tuple, generation_time: int, mko_json: str):
    URI, username, claim_check = post_args
    # print("posting {}".format(mko_json))
    # print("took {} ms".format(generation_time*1000))
    # post_result_cache(args.URI, args.username, args.claim_check, 1000*generation_time, mko_json)

def get_post_args(args: argparse.Namespace):
    return (args.URI, args.username, args.claim_check)

def load_json(json_file: str) -> dict:
    if json_file == None:
        raise InputException("json file")

    if not os.path.exists(json_file):
        raise FileNotFoundError('file "{}" not found'.format(json_file))

    with open(json_file, 'r') as file:
        return file.read()

def train(args: argparse.Namespace):
    train_mko(args.json_file[0], get_post_args(args))

def train_mko(mko: str, post_args: tuple):
    prev_time = time.time()
    mko = MKO.from_json(load_json(mko))
    mko.compile()
    mko.load_data()
    mko.train()
    mko_json = mko.get_json()
    generation_time = time.time() - prev_time
    post(post_args, generation_time, mko_json)

def create(args: argparse.Namespace):
    create_mko(args.name, get_post_args(args))

def create_mko(model_name: str, post_args: tuple):
    prev_time = time.time()
    mko_json = MKO.from_empty(model_name).get_json()
    generation_time = time.time() - prev_time
    post(post_args, generation_time, mko_json)

def add(args: argparse.Namespace):
    add_mko(args.json_file[0], args.add[0].lower(), args.add[1], get_post_args(args))

def add_mko_create_file(mko: str, add_type: str, to_add: str, post_args: tuple):
    file = TempFile("w", delete=False)
    file.write(to_add)
    file.close()
    add_loc = file.name
    add_mko(mko, add_type, add_loc, post_args)
    os.unlink(add_loc)

def add_mko(mko: str, add_type: str, add_loc: str, post_args: tuple):
    prev_time = time.time()
    mko = MKO.from_json(load_json(mko))
    to_add = load_json(add_loc)
    if add_type not in AddTypes.types:
        raise InvalidArgument("add type", AddTypes.types)

    if add_type == AddTypes.DATA:
        mko.add_data(to_add)
    elif add_type == AddTypes.HYPER_PARAMS or add_type == AddTypes.HYPER_PARAMS_ABBREV:
        mko.add_hyper_params(to_add)
    elif add_type == AddTypes.TOPOLOGY:
        mko.add_topology(to_add)

    mko_json = mko.get_json()
    generation_time = time.time() - prev_time
    post(post_args, generation_time, mko_json)


def main():
    args = parse_args()
    print(args)

    if args.add != None:
        add(args)
    if args.function == "create":
        create(args)
    elif args.function == "train":
        train(args)

if __name__ == '__main__':
    main()