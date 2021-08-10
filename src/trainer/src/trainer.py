from sys import exit
from mko import MKO
from network.model import Model
from utilities import get_config

c = get_config()

mko = MKO(c)
assert(mko.topological)
assert(mko.augmented)

model = Model(mko)

model.compile()
model.train()

model.evaluate()
mko = MKO.from_Model(model)

mko.save(c)
exit(0)