from contextlib import contextmanager
from pathlib import Path

import os

@contextmanager
def in_directory(path: Path):
  """ Sets the cwd within the context
  
  Args:
    path (Path): the path to the new cwd
    
  Yields:
    None
  """

  origin = Path().absolute()
  try:
    os.chdir(path)
    yield
  finally:
    os.chdir(origin)