import os, sys
import unittest

import Tests.helpers
from utilities import get_config
from mko import MKO
from network.model import Model

class NetworkTestCase(unittest.TestCase):

  testInputFile = "/tmp/testInput.json"

  def setUp(self):
    Tests.helpers.create_test_input(filename=self.testInputFile)

  def tearDown(self):
    os.remove(self.testInputFile)

  # Test ability to create model from MKO
  def test_mko_from_config(self):
    c = get_config(filename=self.testInputFile)

    mko = MKO(c)
    self.assertTrue(mko.topological)
    self.assertTrue(mko.augmented)
    self.assertFalse(mko.parameterized)
  
  def test_model_from_mko(self):
    c = get_config(filename=self.testInputFile)
    mko = MKO(c) 

    model = Model(mko)