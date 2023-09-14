import time
import numpy as np

def para_run(process_query, coreNum):
    """
    Process management
    param:
        process_query: Generator; consistant of multiprocess.Process
        coreNum: the number of available cpu
    """
    process_running = []

    for _ in range(coreNum):
        p = next(process_query)
        process_running.append(p)
        p.start()

    while True:
        fin = False
        time.sleep(30)

        while sum(p.is_alive() for p in process_running) < coreNum:
            # clear task
            for _ in process_running:
                if not _.is_alive():
                    _.terminate()
            try:
                p = next(process_query)
            except Exception:
                fin = True
                break

            process_running.append(p)
            p.start()

        if fin:
            break

    # wait task finish
    while sum(p.is_alive() for p in process_running) != 0:
        time.sleep(30)
    return 0

class process_saver():
    def __init__(self):
        self.process = []
        self.core = []
        self.run_number = 0

    def append(self,process,core_num):
        self.process.append(process)
        self.core.append(core_num)

    def add(self,count):
        self.run_number += count

    def reduce(self,count):
        self.run_number -= count

    def update(self):
        # Record avliable core number
        release_core = 0
        new_process = []
        new_core = []
        for p, c in zip(self.process, self.core):
            if not p.is_alive():
                p.terminate()
                release_core += c
            else:
                new_process.append(p)
                new_core.append(c)

        self.process = new_process
        self.core = new_core

        return release_core

    def end(self):
        if np.sum([p.is_alive() for p in self.process]) != 0:
            return False
        else:
            return True
