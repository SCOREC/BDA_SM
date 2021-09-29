import os, sys
import unittest
import numpy as np

import Tests.helpers
from utilities import get_config
from mko import MKO
from network.model import Model

class EncapsulationTestCase(unittest.TestCase):

  testInputFile = "/tmp/testInput.json"

  def setUp(self):
    Tests.helpers.create_test_input(filename=self.testInputFile)

  def tearDown(self):
    os.remove(self.testInputFile)

  # Test ability to load config
  def test_load_config(self):
    c = get_config(filename=self.testInputFile)
    self.assertIsNotNone(c)
  
  # Test ability to create model from MKO
  def test_mko_from_config(self):
    c = get_config(filename=self.testInputFile)

    mko = MKO(c)
    self.assertTrue(mko.topological)
    self.assertTrue(mko.augmented)
    self.assertFalse(mko.parameterized)
  
  def test_mko_save(self):
    c = get_config(filename=self.testInputFile)
    mko = MKO(c) 

    mko.save(None, filename="/tmp/tmp.mko")

  def test_mko_load(self):
    c = get_config(filename=self.testInputFile)
    mko = MKO(c) 
    mko.save(None, filename="/tmp/tmp.mko")

    mko = MKO.load(filename="/tmp/tmp.mko")