import json
import argparse
from sys import stdin
import analysis
from analyzers.src.request_manager import SamplerRequestManager
from request_manager import RCRequestManager
import numpy as np

def get_arg(field, args, dtype=None, json_loads=False):
    if field not in args:
        raise Exception("'{}' not in stdin args".format(field))

    result = args[field]
    
    if json_loads:
        assert dtype != None

    if dtype == None:
        return result

    try:
        if not json_loads:
            return dtype(result)
        else:
            return dtype(json.loads(result))
    except Exception:
        raise Exception("'{}' not of type '{}'".format(field, dtype))

def get_stdin_args():
    stdin_args = "\n".join(stdin.readlines())
    return json.loads(stdin_args)

def get_rc_manager(args):
    rc_uri = get_arg("rc_uri", args)
    username = get_arg("username", args)
    claim_check = get_arg("claim_check", args)
    return RCRequestManager(rc_uri, username, claim_check)

def get_sampler_manager(args):
    sampler_uri = get_arg("sampler_uri", args)
    mko = get_arg("model_mko", args)
    return SamplerRequestManager(sampler_uri, mko)

def parse_args():
    parser = argparse.ArgumentParser(description='Run analysis using mko')
    parser.add_argument('--sample',     dest='function', action='store_const', const=sample,     default=None, help='flag for sampling')
    parser.add_argument('--stats',      dest='function', action='store_const', const=stats,      help='flag for stats')
    parser.add_argument('--integrate',  dest='function', action='store_const', const=integrate,  help='flag for integration')
    parser.add_argument('--matplotlib', dest='function', action='store_const', const=matplotlib, help='flag for matplotlib')
    return parser.parse_args(), parser


def sample(args, rc_manager, sampler_manager):
    data_array = get_arg("data_array", args, np.array, True)
    samples_num = get_arg("samples_num", args, int)
    output = analysis.sample(sampler_manager, data_array, samples_num)
    rc_manager.put_result(output)

def stats(args, rc_manager, sampler_manager):
    data_array = get_arg("data_array", args, np.array, True)
    output = analysis.stats(sampler_manager, data_array)
    rc_manager.put_result(output)

def integrate(args, rc_manager, sampler_manager):
    data_array = get_arg("data_array", args, np.array, True)
    funct_table = get_arg("function_table", args, np.array, True)
    samples_num = get_arg("samples_num", args, int)
    output = analysis.integrator(sampler_manager, data_array, samples_num, funct_table)
    rc_manager.put_result(output)

def matplotlib(args, rc_manager, sampler_manager):
    data_array_list = get_arg("data_array_list", args, np.array, True)
    plot_control = get_arg("plot_control", args)
    output = analysis.matplotlib(sampler_manager, data_array_list, plot_control)
    rc_manager.put_result(output)

def main():
    inp_args, parser = parse_args()
    funct = inp_args.function

    if funct == None:
        parser.print_help()
        raise Exception("no behavior specified")

    stdin_args = get_stdin_args()
    rc_manager = get_rc_manager(stdin_args)
    sampler_manager = get_sampler_manager(stdin_args)
    funct(stdin_args, rc_manager, sampler_manager)

if __name__ == "__main__":
    main()