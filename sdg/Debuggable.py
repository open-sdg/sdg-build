import time

class Debuggable:
    """Allows subclasses to print debug statements."""


    def __init__(self, verbose=False):
        self.verbose = verbose


    def debug(self, message):
        if self.verbose:
            message = message.format(
                class_name=type(self).__name__,
            )
            print(Debuggable.get_timestamp() + ' - ' + message)


    @staticmethod
    def get_timestamp():
        start_time = getattr(Debuggable.get_timestamp, 'start_time', None)
        if start_time is None:
            start_time = time.time()
            Debuggable.get_timestamp.start_time = start_time
        elapsed = time.time() - start_time
        return time.strftime("%H:%M:%S", time.gmtime(elapsed))
