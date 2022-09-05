from tensorflow.keras import backend as K
from common.ml import StatusCallback

def compile_model(model, hypers):

  model.compile(loss=hypers['loss_function'], optimizer=hypers['optimizer'])
  K.set_value(model.optimizer.learning_rate, hypers['learning_rate'])
  return model


def fit_model(model, X_train, Y_train, X_test, Y_test, hypers, status_poster):

  callbacks = [StatusCallback(status_poster, hypers['epochs'])]

  model.fit(
    X_train,
    Y_train,
    epochs=hypers['epochs'],
    batch_size=hypers['batch_size'],
    callbacks=callbacks
  )

  loss = model.evaluate(
    X_test,
    Y_test,
    batch_size=hypers['batch_size'],
  )

  hypers['trained'] += hypers['epochs']

  return model, loss