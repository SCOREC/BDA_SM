import numpy as np
from tensorflow.keras import backend as K
from common.ml.callback import StatusCallback, DecayScheduler
from math import log10

def compile_model(model, hypers):

  model.compile(loss=hypers['loss_function'], optimizer=hypers['optimizer'])
  K.set_value(model.optimizer.learning_rate, hypers['learning_rate'])
  return model


def fit_model(model, X_train, Y_train, X_test, Y_test, hypers, status_poster):

  callbacks = [StatusCallback(status_poster, hypers['epochs'])]

  if "lr_schedule" in hypers:
    scheduler = DecayScheduler(hypers["lr_schedule"])
    callbacks.append(scheduler)

  history = model.fit(
    X_train,
    Y_train,
    epochs=hypers['epochs'],
    batch_size=hypers['batch_size'],
    callbacks=callbacks,
    verbose=2,
  )

  loss = model.evaluate(
    X_test,
    Y_test,
    batch_size=hypers['batch_size'],
    verbose=2,
  )

  hypers['trained'] += hypers['epochs']

  return model, loss, history


def mu(rho, model, X_train, Y_train, hypers, test_set):

  for layer in model.layers:
    if hasattr(layer, 'variational'):
      setattr(layer, 'rate', 1.0-rho)
  model.compile(loss=hypers['loss_function'], optimizer=hypers['optimizer'])
  model.fit(X_train, Y_train, epochs=hypers['epochs'], batch_size=hypers['batch_size'])
  samples = model.predict(test_set)
  return samples.std(axis=0)

def autocalibrate_model(model, X_train, Y_train, hypers, topology, status_poster,
                        calibration_point, iterations=5, mix=0.1, desired_mu=1.0, index=0, n_samples=1000):

  current_model = model
  rhos = []
  for layer in topology:
    if layer['type'] == "variational_dropout":
      rhos.append(1.0 - float(layer['rate']))
  if len(rhos) < 1:
    raise Exception("Cannot autocalibrate with no variational layers")
  test_set = np.array(calibration_point, dtype=np.float64).reshape(1,-1)
  test_set = test_set.repeat(int(n_samples), axis=0)
  current_rho = sum(rhos)/float(len(rhos))

  def update_rho(current_rho):
    current_mu = mu(current_rho, current_model, X_train, Y_train, hypers, test_set)[index]
    if current_mu < desired_mu:
      if current_rho < 0.25:
        far_rho = min( 2.0 * current_rho, 0.40 )
      else:
        raise Exception
    elif current_mu > desired_mu:
      far_rho = desired_mu / current_mu * current_rho
    else: #yay!
      return current_rho
    far_mu = mu(far_rho, current_model, X_train, Y_train, hypers, test_set)[index]
    log10_new_rho = (log10(far_rho) - log10(current_rho)) / (far_mu - current_mu) * (desired_mu - current_mu) + log10(current_rho)

    return 10**log10_new_rho
  
  
  for i in range(max(1,iterations)):
    new_rho = update_rho(current_rho)
    new_rho = new_rho * (1.0 - mix)  + current_rho * mix
    status_poster(float(i) / float(iterations))
  
  return current_model, new_rho