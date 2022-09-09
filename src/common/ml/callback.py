from tensorflow.keras.callbacks import Callback

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