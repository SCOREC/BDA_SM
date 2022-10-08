from tensorflow.keras.callbacks import Callback, LearningRateScheduler

class StatusCallback(Callback):
  def __init__(self, status_poster, total_epochs: int):
    super().__init__()
    self._status_poster = status_poster
    self.total_epochs = total_epochs
    self._last_status = 0.0

  def on_epoch_end(self, epoch, logs=None):
    status = epoch / self.total_epochs
    if status == 1:
        status -= 1E-6
    if status - self._last_status > 0.05:
        self._last_status = status
        self._status_poster(status)

class DecayScheduler(LearningRateScheduler):
  def __init__(self, decay_schedule):
    self.decay_schedule = decay_schedule
    super().__init__(self.decay)

  def decay(self, epoch):
    new_lr = self.decay_schedule[0][1]
    for lim, lr in self.decay_schedule:
      if epoch >= lr:
        new_lr = lr
    return new_lr
  
