from typing import Optional

class InputException(Exception):
    def __init__(self, field: str, type_error: Optional[tuple] = None):
        if type_error == None:
            super().__init__("field '{}' not in input json".format(field))
        else:
            super().__init__("field '{}' not of type '{}' instead is type '{}'".format(field, type_error[0], type_error[1]))

class InvalidArgument(Exception):
    def __init__(self, argument: str, valid_arguments: list):
        super().__init__("argument '{}' supplied is not in valid arguments '{}'".format(argument, valid_arguments))

class VersionException(Exception):
    def __input__(self, source_version: str, json_version: str):
        super().__init__("source version {} != json version {}".format(source_version, json_version))