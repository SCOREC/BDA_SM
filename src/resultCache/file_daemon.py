from genericpath import exists
from threading import Thread, Event
from sched import scheduler
import time
import json
import os
from typing import Union


class PurgeDaemon(Thread):
    def __init__(self, min_expiry_time, schedule_location="./schedule.json"):
        super(PurgeDaemon, self).__init__()
        self._should_stop = Event()
        self._scheduler = scheduler(time.time, time.sleep)
        self._schedule_location = schedule_location
        self._min_expiry_time = min_expiry_time
        self.file_lock = set()
        self.load_schedule()

    def save_schedule(self):
        to_save = []
        for event in self._scheduler.queue:
            delete_time = (event.argument[1], event.time)
            to_save.append(delete_time)

        with open(self._schedule_location, "w") as file:
            json.dump(to_save, file)

    def load_schedule(self):
        if not os.path.exists(self._schedule_location):
            return
        
        with open(self._schedule_location, "r") as file:
            load_schedule = json.load(file)

        for event in load_schedule:
            self.add_entry(event[0], event[1])

    def delete(self, location: str, override_lock: bool = False) -> bool:
        while not override_lock and location in self.file_lock:
            time.sleep(0.01)

        if not os.path.exists(location):
            return False

        if not override_lock:
            self.file_lock.add(location)
        os.remove(location)
        if not override_lock:
            self.file_lock.remove(location)

        parent_folder = os.path.dirname(location)
        
        while parent_folder in self.file_lock:
            time.sleep(0.01)

        if len(os.listdir(parent_folder)) == 0:
            self.file_lock.add(parent_folder)
            os.rmdir(parent_folder)
            self.file_lock.remove(parent_folder)

        return True

    def update_scheduler(self):
        self._scheduler.run(blocking=False)

    def run(self):
        while not self._should_stop.is_set():
            self.update_scheduler()
            self.save_schedule()
            self._should_stop.wait(self._min_expiry_time)

    def end(self):
        self._should_stop.set()
        self.join()

    def add_to_delete(self, location: str):
        self.delete(location)

    def add_entry(self, location: str, expiry_time: int):
        self._scheduler.enterabs(expiry_time, 1, PurgeDaemon.add_to_delete, argument=(self, location))
        self.save_schedule()

    def remove_entry(self, location: str) -> bool:
        event = None
        for entry in self._scheduler.queue:
            if entry.argument[1] == location:
                event = entry

        if event:
            self._scheduler.cancel(event)
            self.save_schedule()
            return True

        return False

    def delete_all(self, delete_schedule=False):
        for entry in self._scheduler.queue:
            loc = entry.argument[1]
            self._scheduler.cancel(entry)
            self.delete(loc)

        self.save_schedule()

        if delete_schedule:
            os.remove(self._schedule_location)


class FileHandler:
    def __init__(self, min_expiry_time, max_expiry_time, root_directory: str = "."):
        if os.path.isabs(root_directory):
            self._directory = root_directory
        else:
            self._directory = os.path.join(os.getcwd(), root_directory)

        self._min_expiry_time = min_expiry_time
        self._max_expiry_time = max_expiry_time

        schedule_location = os.path.join(self._directory, "schedule.json")
        self._purge_daemon = PurgeDaemon(min_expiry_time, schedule_location)
        self._purge_daemon.start()


    def end(self):
        self._purge_daemon.end()

    def get_file_location(self, username: str, claim_check: str, create_folders: bool = False) -> str:
        username_folder = os.path.join(self._directory, username)

        if create_folders:
            while username_folder in self._purge_daemon.file_lock:
                time.sleep(0.01)
            
            self._purge_daemon.file_lock.add(username_folder)
            os.makedirs(username_folder, exist_ok=True)
            self._purge_daemon.file_lock.remove(username_folder)

        return os.path.join(username_folder, claim_check)
 
    def get_expiry_time(self, generation_time) -> int:
        return min(5 * generation_time + self._min_expiry_time, self._max_expiry_time)

    def put(self, username: str, claim_check: str, generation_time: int, data: Union[bytes, str]):
        expiry_time = self.get_expiry_time(generation_time) + time.time()
        location = self.get_file_location(username, claim_check, create_folders=True)

        mode = "w"
        if type(data) == bytes:
            mode = "wb"

        with open(location, mode) as file:
            file.write(data)

        self._purge_daemon.add_entry(location, expiry_time)


    def get(self, username: str, claim_check: str, type: type) -> Union[bytes, str]:
        location = self.get_file_location(username, claim_check)

        while location in self._purge_daemon.file_lock:
            time.sleep(0.01)

        if not os.path.exists(location):
            return None

        self._purge_daemon.file_lock.add(location)
        self._purge_daemon.remove_entry(location)

        mode = "r"
        if type == bytes:
            mode = "rb"

        with open(location, mode) as file:
            data = file.read()

        self._purge_daemon.delete(location, True)
        self._purge_daemon.file_lock.remove(location)


        return data

    def delete_all(self, delete_schedule=False):
        self._purge_daemon.delete_all(delete_schedule)
        