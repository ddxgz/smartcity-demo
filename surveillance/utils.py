import functools
import time
import logging

# logging.basicConfig(level=logging.DEBUG)


def funclogger(text):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logging.info('%s start func[%s]' % (text, func.__name__))
            start = time.time()
            result = func(*args, **kwargs)
            interval = time.time() - start
            logging.info('%s end func[%s], running: %0.5f seconds' % (text,
                func.__name__, interval))
            return result
        return wrapper
    return decorator


def time2Stamp(timestr, format_type='%m/%d/%Y %H:%M:%S'):
    return time.mktime(time.strptime(timestr, format_type))


def stamp2Time(stamp, format_type='%m/%d/%Y %H:%M:%S'):
    return time.strftime(format_type, time.localtime(stamp))


print(stamp2Time(1433382656))