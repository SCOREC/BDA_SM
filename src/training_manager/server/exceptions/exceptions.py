
class RCException(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class InputException(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)