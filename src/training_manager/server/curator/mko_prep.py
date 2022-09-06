from common.mko  import MKO
from server.externals.results_cache import get_new_claim_check, post_results_cache
import server.curator.defaults as defaults

def create_mko(model_name, username):
  mko = MKO(model_name)
  claim_check = get_new_claim_check(username, offset=10)
  post_results_cache(username, claim_check, 1.0, str(mko))
  return claim_check

# TODO - Implementing this shows me I don't need a separate create_mko.
def fill_mko(username, model_name, old_mko, dataspec, topology, hypers):

  mko = MKO.from_base64(old_mko)
  data = {
    'dataspec': defaults.dataspec,
    'hypers': defaults.hypers,
    'topology': defaults.topology
  }

  data['model_name'] = model_name

  data['dataspec'].update(dataspec)
  if len(topology) > 0: data['topology'] = topology
  data['hypers'].update(hypers)

  mko = MKO.from_dict(data)

  claim_check = get_new_claim_check(username, offset=10)
  post_results_cache(username, claim_check, 1.0, str(mko))
  return claim_check

