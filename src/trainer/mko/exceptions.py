from typing import Optional, Tuple

class UserError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
        pass

class InputException(UserError):
    def __init__(self, field: str, type_error: Optional[Tuple[type, type]] = None):
        if type_error == None:
            super().__init__("field '{}' not in input".format(field))
        else:
            super().__init__("field '{}' not of type '{}' instead is type '{}'".format(field, str(type_error[0]), str(type_error[1])))

class InvalidArgument(UserError):
    def __init__(self, argument: str, valid_arguments: list):
        super().__init__("argument '{}' supplied is not in valid arguments '{}'".format(argument, valid_arguments))

class VersionException(UserError):
    def __init__(self, source_version: str, json_version: str):
        super().__init__("source version {} != json version {}".format(source_version, json_version))

class MKOTypeException(UserError):
    def __init__(self, expected_type: str):
        super().__init__("expected MKO type of '{}'".format(expected_type))