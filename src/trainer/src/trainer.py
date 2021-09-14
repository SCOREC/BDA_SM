from sys import exit
from mko import MKO
from tensorflow import keras as keras
from network.model import Model
from utilities import get_config

c = get_config()

mko = MKO(c)
assert(mko.topological)
assert(mko.augmented)

(x_test, y_test) = mko.testing_data

model = Model(mko)
print("model is type:{}".format(type(model)))
model.compile()
model.train()
model.evaluate()
mko2 = MKO.from_Model(model)
mod2 = Model(mko2)
print("mod2 is type:{}".format(type(mod2)))
mod2.describe()
mod2.evaluate()
mod2.summary()
exit(0)

model.evaluate()
mko = MKO.from_Model(model)
model = Model(mko)

model.compile()
model.evaluate()

mko.save(c)

model2 = Model(mko)


exit(0)