from external_query import post_status
from tensorflow.keras.callbacks import Callback

class StatusCallback(Callback):
    def __init__(self, post_args: tuple, total_epochs: int):
        super().__init__()
        self.post_args = post_args 
        self.total_epochs = total_epochs

    def on_epoch_end(self, epoch, logs=None):
        status = epoch / self.total_epochs
        if status == 1:
            status -= 1E-6
        post_status(*self.post_args, status)