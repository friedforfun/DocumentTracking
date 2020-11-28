from copy import deepcopy
import json
import threading
import queue
from alive_progress import alive_bar
from DocuTrace.Utils.Logging import logger, debug, logging
import time

def stream_file_chunks(file_name, chunk_size=100000):
    with open(file_name) as f:
        while True:
            data = f.readlines(chunk_size)
            if not data:
                break
            yield data

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
    def __init__(self, path=None,  chunk_size=100000):
        if path is not None:
            self.file_iter = stream_file_chunks(path, chunk_size=chunk_size)
        else:
            self.file_iter = None
        self.path = path

        self.parsed_file = False

    def set_read_path(self, path, chunk_size=100000):
        """Specify the path for LocationViews to read from

        Args:
            path (str): Path to the datafile
        """
        self.file_iter = stream_file_chunks(path, chunk_size=chunk_size)

    @debug
    def parse_file(self, data_collector, threaded=False, num_threads=4):
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
        #with alive_bar() as bar:
        if threaded:
            logger.warning('Threading has been enabled in FileRead.parse_file, this is experimental and may result in worse performance with small files.')
            with JsonThreadsContextManager(data_collector, num_threads) as jtcm:
                for chunk in self.file_iter:
                    jtcm.enqueue(chunk)
                    #bar()
                logger.debug('Finished queueing chunks')
        else:

            for chunk in self.file_iter:
                for line in chunk:
                    try:
                        json_line = line.rstrip()
                        parsed_json = json.loads(json_line)
                        [fn(parsed_json) for fn in self.fn_list]
                    except json.JSONDecodeError as e:
                        logger.exception(
                            'JSON decode error encountered in thread: main. Exception: {}'.format(e))
                        #bar()

        logger.debug('End reading file: {}'.format(self.path))

class JsonThreadsContextManager():
    """Context manager to assist processing large files with threads

        Args:
            data_collector (DataCollector): An instance of the DataCollector class
            num_threads (int): The number of threads to instantiate
        """
    def __init__(self, data_collector, num_threads):
        self.queue = queue.Queue()
        self.data_collector = data_collector
        self.collectors = [deepcopy(data_collector) for _ in range(num_threads)]
        self.threads = self.assign_threads([JsonParseThread(i, self.collectors[i]) for i in range(num_threads)])

    def assign_threads(self, threads):
        """Assign each thread a reference to the queue

        Args:
            threads (JsonParseThread): A thread to parse the json file

        Returns:
            list(JsonParseThread): A list of threads
        """
        self.threads = [thread.set_queue(self.queue) for thread in threads]
        return self.threads

    def enqueue(self, chunk):
        """Add a chunk to the queue to be processed by consumer threads

        Args:
            chunk (list(str)): A chunk produced by the stream_file_chunks function
        """
        self.queue.put(chunk)

    def __enter__(self):
        [t.start() for t in self.threads]
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if exception_value is not None:
            logger.debug('Exception when leaving context manager: {}'.format(exception_type))
        self.queue.join()
        for collector in self.collectors:
            self.data_collector.merge(collector)


class JsonParseThread(threading.Thread):
    def __init__(self, name, data_collector):
        threading.Thread.__init__(self)
        self.t_name = name
        self.data_collector = data_collector
        self.fn_list = data_collector.data_fns

    def set_queue(self, queue):
        """Assign a reference to the queue to consume from

        Args:
            queue (queue.Queue): A FIFO queue working as a provider for each thread

        Returns:
            JsonParseThread: Self with a queue assigned
        """
        self.queue = queue
        return self

    def run(self):
        logger.debug('Thread: {} - running'.format(self.t_name))
        while True:
            chunk = self.queue.get()
            start_time = time.time()
            #print('CHUNK SIZE: {}'.format(len(chunk)))
            for line in chunk:
                try:
                    json_line = line.rstrip()
                    parsed_json = json.loads(json_line)
                    [fn(parsed_json) for fn in self.fn_list]
                except json.JSONDecodeError as e:
                    logger.exception('JSON decode error encountered in thread: {}. Exception: {}'.format(self.t_name, e))
            self.queue.task_done()
            duration = time.time() - start_time
            logger.debug('Thread <{}>... one chunk processed. Duration: {} | Chunk size: {}'.format(self.t_name, duration, len(chunk)))
        
