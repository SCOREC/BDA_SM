import unittest
import Tests.testdata as td
import jwt
import server.trainer as trainer
import time
import Tests.helpers

class TrainerLinksTestCase(unittest.TestCase):
  def __init__(self, methodName: str = ...) -> None:
    super().__init__(methodName)
    pass

  def test_create_mko(self):

    claim_check = trainer.create_mko(td.good_modelname, td.good_username)

    cc_data = jwt.decode(claim_check, options={"verify_signature": False})

    self.assertIn("eta", cc_data)
    self.assertIn("username", cc_data)
    self.assertEqual(cc_data['username'], td.good_username)

    time.sleep(5)

    mko = Tests.helpers.redeem_claim_check(td.good_username, claim_check)
    mko_json = Tests.helpers.json_from_mko_string(mko)

    self.assertIn("model_name", mko_json)
    self.assertEqual(mko_json['model_name'], td.good_modelname)

  def test_fill_mko(self):

    dataspec = td.dataspec
    claim_check = trainer.fill_mko(td.good_username, td.good_modelname, td.stage1mko, dataspec)

    cc_data = jwt.decode(claim_check, options={"verify_signature": False})

    self.assertIn("eta", cc_data)
    self.assertIn("username", cc_data)
    self.assertEqual(cc_data['username'], td.good_username)

    time.sleep(5)
    status = Tests.helpers.get_claim_check_status(td.good_username, claim_check)
    status = float(status)
    self.assertGreaterEqual(status, 0.0)
    self.assertLessEqual(status, 1.0)

    time.sleep(1)
    mko = Tests.helpers.redeem_claim_check(td.good_username, claim_check)
    print("MKO:\n", mko)
    mko_json = Tests.helpers.json_from_mko_string(mko)

    #print("MKO KEYS", list(mko_json.keys()))
    self.assertIn("model_name", mko_json)
    self.assertEqual(mko_json['model_name'], td.good_modelname)
    self.assertEqual(mko_json['data']['x_tags'], dataspec['x_tags'])

  def test_train_mko(self):

    max_iterations = 10
    iteration_sleep = 10

    smip_token = Tests.helpers.get_bearer_token(
      td.smip_auth['url'],
      td.smip_auth['authenticator'],
      td.smip_auth['role'],
      td.smip_auth['password']
      )
    
    claim_check = trainer.train_mko(td.good_username, td.good_modelname, td.stage2mko, smip_token, td.smip_auth['url'])

    cc_data = jwt.decode(claim_check, options={"verify_signature": False})

    self.assertIn("eta", cc_data)
    self.assertIn("username", cc_data)
    self.assertEqual(cc_data['username'], td.good_username)

    time.sleep(10)
    status = Tests.helpers.get_claim_check_status(td.good_username, claim_check)
    status = float(status)
    n_iterations = 0
    while status < 1.0 and n_iterations < max_iterations:
      self.assertGreaterEqual(status, 0.0)
      self.assertLessEqual(status, 1.0)
      time.sleep(iteration_sleep)
      status = Tests.helpers.get_claim_check_status(td.good_username, claim_check)
      status = float(status)
      n_iterations += 1

    self.assertTrue(n_iterations < max_iterations or status >= 1.0)
    time.sleep(1)
    mko = Tests.helpers.redeem_claim_check(td.good_username, claim_check)
    mko_json = Tests.helpers.json_from_mko_string(mko)

    #print("MKO KEYS", list(mko_json.keys()))
    self.assertIn("model_name", mko_json)
    self.assertEqual(mko_json['model_name'], td.good_modelname)




    



    