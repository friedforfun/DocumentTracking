import json
from DocuTrace.Utils.Logging import logger
import threading, queue
#from multiprocessing import Queue

def stream_read_json(fname):
    """Lazy read json generator
    https://stackoverflow.com/questions/6886283/how-i-can-i-lazily-read-multiple-json-values-from-a-file-stream-in-python

    Args:
        fname (str): The file name to read

    Yields:
        JSONDecoder: Deserialized JSON as python object
    """
    start_pos = 0
    with open(fname, 'r') as f:
        while True:
            try:
                obj = json.load(f)
                yield obj
                return
            except json.JSONDecodeError as e:
                f.seek(start_pos)
                json_str = f.read(e.pos)
                obj = json.loads(json_str)
                start_pos += e.pos
                yield obj


class ParseFile:
    def __init__(self, path=None):
        if path is not None:
            self.file_iter = stream_read_json(path)
        else:
            self.file_iter = None
        self.path = path

        self.parsed_file = False

    def set_read_path(self, path):
        """Specify the path for LocationViews to read from

        Args:
            path (str): Path to the datafile
        """
        self.file_iter = stream_read_json(path)


    def parse_file(self, fn_list, threaded=False, num_threads=1):
        """Apply a list of functions to the file_iter

        Args:
            fn_list (list(dict->None)): A list of functions that all take a dict as a parameter
            threaded (bool, optional): Experimental, currently much slower than without (cost of instantiating threads too great). Defaults to False.

        Raises:
            AttributeError: When a path has not been specified for the file iterator
        """
        if self.file_iter is None:
            raise AttributeError('File iterator not set')
        logger.debug('Begin reading file: {}'.format(self.path))

        if threaded:
            logger.warning('Threading has been enabled in FileRead.parse_file, this is experimental and may result in worse performance.')
            with JsonThreadsContextManager(fn_list, num_threads) as jtcm:
                for json in self.file_iter:
                    jtcm.enqueue(json)
                
        else:
            for json in self.file_iter:
                [fn(json) for fn in fn_list]
        
        logger.debug('End reading file: {}'.format(self.path))

class JsonThreadsContextManager():
    def __init__(self, fn_list, num_threads):
        self.queue = queue.Queue()
        self.threads = self.assign_threads([JsonParseThread(i, fn_list) for i in range(num_threads)])

    def assign_threads(self, threads):
        self.threads = [thread.set_queue(self.queue) for thread in threads]
        return self.threads

    def enqueue(self, json):
        self.queue.put(json)

    def __enter__(self):
        [t.start() for t in self.threads]
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if exception_value is not None:
            logger.debug('Exception when leaving context manager: {}'.format(exception_type))
        self.queue.join()

class JsonParseThread(threading.Thread):
    def __init__(self, name, fn_list):
        threading.Thread.__init__(self, daemon=True)
        self.name = name
        self.fn_list = fn_list

    def set_queue(self, queue):
        self.queue = queue
        return self

    def run(self):
        logger.debug('Thread: {} - running'.format(self.name))
        while True:
            json_line = self.queue.get()
            [fn(json_line) for fn in self.fn_list]
            self.queue.task_done()
        
