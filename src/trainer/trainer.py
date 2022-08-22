import argparse
import os
from externals.results_cache import post_result_cache, post_error
from mko.dan_mko import MKO
from mko.exceptions import InputException, InvalidArgument
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

# command line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Trains an MKO')
    parser.add_argument('-f', nargs=1, dest='file_loc', const=None, default=None, type=str, help='path to file for MKO')
    parser.add_argument('--create', dest='function', action='store_const', const='create', default='create', help='create MKO')
    parser.add_argument('--name', nargs=1, dest='name', default=['model'], help='name of model')
    parser.add_argument('--add', nargs=2, dest='add', help='add to MKO file, first args is type second is location')
    parser.add_argument('--train', dest='function', action='store_const', const='train', help='train MKO object')
    parser.add_argument('username', metavar='username', type=str, help='username of user')
    parser.add_argument('claim_check', metavar='claim_check', type=str, help='claim_check to store in result_cache')
    parser.add_argument('URI', metavar='rc_URI', type=str, help='URI of the result cache')
    parser.add_argument('--delete', dest='delete', action='store_const', const='false', default='false', help='should delete file after usage')
    return parser.parse_args()

def delete_file(file_loc: str):
    if not os.path.exists(file_loc):
        return

    os.unlink(file_loc)


# post_args: tuple of command line arguments (URI, username, claim_check)
# generation_time: seconds to generate
# mko_data: data to send to resultCache
def post(post_args: tuple, generation_time: int, mko_data: str):
    URI, username, claim_check = post_args
    post_result_cache(URI, username, claim_check, generation_time, mko_data)

# converts command line parser to tuple
def get_post_args(args: argparse.Namespace):
    return (args.URI, args.username, args.claim_check)

# loads file
def load_file(file_loc: str) -> dict:
    if file_loc == None:
        raise InputException("file_loc")

    if not os.path.exists(file_loc):
        raise FileNotFoundError('file "{}" not found'.format(file_loc))

    with open(file_loc, 'r') as file:
        return file.read()

# args: command line parser
# trains model according to args
def train(args: argparse.Namespace):
    train_mko(
        args.file_loc[0], 
        get_post_args(args), 
        False if args.delete.lower() == 'false' else True
    )

# mko: file location of mko
# post_args: (URI, usernae, claim_check)
def train_mko(mko_filename: str, post_args: tuple, delete: bool):
    prev_time = time.time()
    mko = MKO.from_b64str(load_file(mko_filename))
    mko.compile()
    mko.load_data()
    mko.train(push_update_args=post_args)
    mko_data = str(mko)
    generation_time = time.time() - prev_time
    post(post_args, generation_time, mko_data)

    if delete:
        delete_file(mko)

# args: command line parser
# creates new mko given the name
def create(args: argparse.Namespace):
    create_mko(args.name[0], get_post_args(args))

# model_name: name of the new model
# post_args: (URI, usernae, claim_check)
# creates new mko and posts to resultCache
def create_mko(model_name: str, post_args: tuple):
    prev_time = time.time()
    mko_data = str(MKO.from_empty(model_name))
    generation_time = time.time() - prev_time
    post(post_args, generation_time, mko_data)

# args: command line parser
# adds a json object to the mko
def add(args: argparse.Namespace):
    add_mko(
        args.file_loc[0], 
        args.add[0].lower(), 
        args.add[1], get_post_args(args), 
        False if args.delete.lower() == 'false' else True
    )

# mko: file location of mko
# add_type: portion of mko to append to (data, hyperparams, etc.)
# to_add: location of new json file to merge with mko
# post_args: (URI, usernae, claim_check)
# combines to_add as a sub field of mko under the to_add tag
def add_mko(mko_filename: str, add_type: str, add_loc: str, post_args: tuple, delete: bool):
    prev_time = time.time()
    mko = MKO.from_b64str(load_file(mko_filename))
    print("Loaded MKO from ", mko_filename)
    to_add = load_file(add_loc)
    if add_type not in AddTypes.types:
        raise InvalidArgument("add type", AddTypes.types)

    if add_type == AddTypes.DATA:
        mko.add_data(to_add)
    elif add_type == AddTypes.HYPER_PARAMS or add_type == AddTypes.HYPER_PARAMS_ABBREV:
        mko.add_hyper_params(to_add)
    elif add_type == AddTypes.TOPOLOGY:
        mko.add_topology(to_add)

    mko_data = str(mko)
    generation_time = time.time() - prev_time
    post(post_args, generation_time, mko_data)
    
    if delete:
        delete_file(mko)
        delete_file(add_loc)


def main():
    args = parse_args()

    try:    
        if args.add != None:
            add(args)
        elif args.function == "create":
            create(args)
        elif args.function == "train":
            train(args)
    except Exception as e:
        post_error(*get_post_args(args), str(e))
        raise e

if __name__ == '__main__':
    main()