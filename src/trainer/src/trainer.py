from sys import exit
from mko import MKO
from network.model import Model
from utilities import getConfig

c = getConfig()

mko = MKO(c)
assert(mko.topological)
assert(mko.augmented)

model = Model(mko)

model.train(c)

mko = model.toMKO(c)

mko.save(c)
exit(0)