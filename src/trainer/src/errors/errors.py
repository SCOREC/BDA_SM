class MKOError(RuntimeError):
  def __init__(self, message):
      super().__init__(self, message)
      self.message = message