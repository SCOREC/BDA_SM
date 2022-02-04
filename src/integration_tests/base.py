from unittest import TestCase
from multiprocessing import Process
from training_manager import app as tm_app
from resultCache import app as rc_app
import logging

class BaseTest(TestCase):
    def setUp(self):
        self.tm_port = 8080
        self.rc_port = 9090
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        tm_app.config["TESTING"] = True
        rc_app.config["TESTING"] = True
        self.tm_process = Process(target=tm_app.run, kwargs={"host": "127.0.0.1", "port": self.tm_port, "debug": False})
        self.tm_process.start()
        self.rc_process = Process(target=rc_app.run, kwargs={"host": "127.0.0.1", "port": self.rc_port, "debug": False})
        self.rc_process.start()

    
    def get_tm(self, formatted_params=""):
        return "http://127.0.0.1:" + str(self.tm_port) + formatted_params

    def get_rc(self, formatted_params=""):
        return "http://127.0.0.1:" + str(self.rc_port) + formatted_params

    def tearDown(self):
        self.tm_process.terminate()
        self.tm_process.join()
        self.rc_process.terminate()
        self.rc_process.join()
        

    