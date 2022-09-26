import threading

import reacton as react


def use_work_threaded(callback, dependencies=[]):
    def run():
        def runner():
            callback()

        threading.Thread(target=runner).start()

    react.use_effect(run, dependencies)
