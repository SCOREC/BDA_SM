import os, sys
import unittest
import numpy as np

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
  def test_mko_construction(self):
    c = get_config(filename=self.testInputFile)

    mko = MKO(c)
    self.assertTrue(mko.topological)
    self.assertTrue(mko.augmented)
    self.assertFalse(mko.parameterized)
  
  def test_model_from_mko(self):
    c = get_config(filename=self.testInputFile)
    mko = MKO(c) 

    model = Model(mko)

  def test_model_compiles(self):
    c = get_config(filename=self.testInputFile)
    mko = MKO(c) 
    model = Model(mko)

    model.compile()
    self.assertIsInstance(model, Model)

  def test_model_trains(self):
    c = get_config(filename=self.testInputFile)
    mko = MKO(c) 
    (x_test, y_test) = mko.testing_data
    model = Model(mko)

    model.compile()
    model.train(verbose=0)

  def test_model_evaluation(self):
    c = get_config(filename=self.testInputFile)
    mko = MKO(c) 
    (x_test, y_test) = mko.testing_data
    model = Model(mko)

    model.compile()
    model.train(verbose=0)
    metrics = model.evaluate(verbose=0)
  
    c = get_config(filename=self.testInputFile)
    mko = MKO(c) 
    (x_test, y_test) = mko.testing_data
    model = Model(mko)

    model.compile()
    model.train(verbose=0)
    (testing_inputs , gold_standard_outputs) = mko.testing_predictions

    for input, gs_output in zip(testing_inputs, gold_standard_outputs):
      input_rows = np.repeat([input], 500, axis=0)
      sampled_outputs = model.predict(input_rows)
      sample_means = np.mean(sampled_outputs, axis=0)
      for i, output in enumerate(sample_means):
        abs_diff = np.abs(output - gs_output[i])
        self.assertLess(abs_diff, 0.1)