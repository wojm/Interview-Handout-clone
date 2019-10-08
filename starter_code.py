import mock_db
import uuid
from worker import worker_main
from threading import Thread, Lock
import time

# Global Lock
lock = Lock()

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

    start_time = time.time()

    # Do While loop with a time-sensitive break condition
    while time.time() < start_time + give_up_after:
        if lock.acquire(False): # non-blocking aquisation of lock
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
