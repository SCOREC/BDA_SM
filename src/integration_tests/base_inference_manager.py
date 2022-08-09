from unittest import TestCase
from multiprocessing import Process
from sampler import app as sampler_app
from inference_manager import app as inference_manager_app
import logging
import time

class BaseTest(TestCase):
    def setUp(self):
        self.sm_port = 5555
        self.im_port = 6666

        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)

        sampler_app.config["TESTING"] = True
        inference_manager_app.config["TESTING"] = True

        self.sm_process = Process(target=sampler_app.run, kwargs={"host": "127.0.0.1", "port": self.sm_port, "debug": False})
        self.sm_process.start()
        self.im_process = Process(target=inference_manager_app.run, kwargs={"host": "127.0.0.1", "port": self.im_port, "debug": False})
        self.im_process.start()
        time.sleep(1)

    
    def get_sm(self, formatted_params=""):
        return "http://127.0.0.1:" + str(self.sm_port) + formatted_params

    def get_im(self, formatted_params=""):
        return "http://127.0.0.1:" + str(self.im_port) + formatted_params

    def get_rc(self, formatted_params=""):
            return "http://127.0.0.1:" + str(self.rc_port) + formatted_params

    def tearDown(self):
        self.sm_process.terminate()
        self.sm_process.join()
        self.im_process.terminate()
        self.im_process.join()
        

    