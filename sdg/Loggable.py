import time

class Loggable:
    """Allows subclasses to print debug statements."""


    def __init__(self, logging=None):
        self.logging = logging


    def warn(self, message, **kwargs):
        if self.logging is not None and 'warn' in self.logging:
            self.log(message, **kwargs)


    def debug(self, message, **kwargs):
        if self.logging is not None and 'debug' in self.logging:
            self.log(message, **kwargs)


    def log(self, message, **kwargs):
        kwargs['class_name'] = type(self).__name__
        message = message.format(**kwargs)
        print(Loggable.get_timestamp() + ' - ' + message)


    @staticmethod
    def get_timestamp():
        start_time = getattr(Loggable.get_timestamp, 'start_time', None)
        if start_time is None:
            start_time = time.time()
            Loggable.get_timestamp.start_time = start_time
        elapsed = time.time() - start_time
        return time.strftime("%H:%M:%S", time.gmtime(elapsed))
