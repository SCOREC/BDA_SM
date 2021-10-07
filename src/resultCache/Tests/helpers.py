import random
import string
from resultCache.config import TestConfig as config

def get_test_set():
        usernames = generate_string(config.num_users_test, config.string_len_test)
        ccs = generate_string(config.num_cc_test, config.string_len_test)
        data = generate_string(config.num_data_files, config.num_characters_data_test)
        return usernames, ccs, data

def generate_string(l, n):
        strings = []
        for _ in range(n):
            gen_string = ''.join(random.choice(string.ascii_letters) for _ in range(l))
            strings.append(gen_string)
        return strings