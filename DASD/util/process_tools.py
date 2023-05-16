import time

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
        # 记录释放出的核数
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
        if sum([p.is_alive() for p in self.process]) != 0:
            return False
        else:
            return True


def para_run(process_query, coreNum):
    """
    进程管理,基于CPU核心数和要执行进程数，对资源进行分配。
    :param process_query: 生成器；包含要执行的进程对象（multiprocess.Process）
    :param coreNum: 被分配给任务的核心数
    :return: 任务全部完成时返回
    """
    process_running = []

    for _ in range(coreNum):
        p = next(process_query)
        process_running.append(p)
        p.start()

    while True:
        fin = False
        time.sleep(30)
        # 入队
        while sum(p.is_alive() for p in process_running) < coreNum:
            # 中止结束的进程
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

    # 等待任务子进程结束
    while sum(p.is_alive() for p in process_running) != 0:
        time.sleep(30)
    return 0