import mock_db
import uuid
from worker import worker_main
from threading import Thread
import time
from random import random

DEBUG = True

rand = random()
class Lock():
    """
    Lock based off db. Insert into db, if first in queue, proceed. 

    Args:
        db : database to connect to
        hash : unique hash to specify this request. Could be defaulted to uuid
    """

    def __init__(self, db, name = ''):
        """
        Connect lock to database
        """
        self.db = db
        self.task_obj = {
            '_id': f'taskID: { name }',
        }
        if DEBUG:
            self.start_timestamp = time.time()
            self.latest_timestamp = self.start_timestamp
            self.miss_count = 0

    def _stop_watch(self, state):
        current_time = time.time()

        print(
            'thread %s after %3.0f misses, in %4.2f seconds since last and %4.2f from the start' \
            % (
                state, 
                self.miss_count, 
                current_time - self.latest_timestamp, 
                current_time - self.start_timestamp
            )
        )

        self.latest_timestamp = current_time
        self.miss_count = 0

    def acquire(self):
        """
        Aquire the lock. Done by adding a record with a set _id, this record will not be added if a record exists
        """
        try:
            self.db.insert_one(self.task_obj)

            if DEBUG:
                self._stop_watch('acquired')

            return True
        except:
            if DEBUG:
                self.miss_count = self.miss_count + 1
            
            return False
    
    def release(self):
        """
        Release the lock. Simply delete entry from database
        """
        if DEBUG:
            self._stop_watch('deleted ')

        self.db.delete_one(self.task_obj)

def attempt_run_worker(worker_hash, give_up_after, db, retry_interval):
    """
        Run the worker from worker.py by calling worker_main

        This function includes logic to retry if the lock is unavailable or if there is an exception. 
        It also includes timeoute logic for all 

        TODO: this function may be better as a higher order function that takes in a function and args 
        for that function, 
        ie attempt_run_worker(fn, args, give_up_after=<default>, retry_interval=<default>)
         - fn = worker_main
         - args = [ worker_hash, db ]
        Also, making this a class would allow lock to be a static class variable

        Args:
            worker_hash: a random string we will use as an id for the running worker
            give_up_after: if the worker has not run after this many seconds, give up
            db: an instance of MockDB
            retry_interval: continually poll the locking system after this many seconds
                            until the lock is free, unless we have been trying for more
                            than give_up_after seconds
    """
    start_timestamp = time.time()

    lock = Lock(db, 'task')
    # Do While loop with a time-sensitive break condition
    while time.time() < start_timestamp + give_up_after:
        if lock.acquire(): # non-blocking acquisation of lock
            try:
                worker_main(worker_hash, db)
                break
            except:
                print('caught exception')
            finally:
                lock.release() # always release block, even if breaking loop

        time.sleep(retry_interval)



if __name__ == "__main__":
    """
        DO NOT MODIFY

        Main function that runs the worker five times, each on a new thread
        We have provided hard-coded values for how often the worker should retry
        grabbing lock and when it should give up. Use these as you see fit, but
        you should not need to change them
    """

    db = mock_db.DB()
    threads = []
    for _ in range(25):
        t = Thread(target=attempt_run_worker, args=(uuid.uuid1(), 2000, db, 0.1))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()
