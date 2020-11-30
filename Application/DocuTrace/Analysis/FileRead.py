from copy import deepcopy
import json
import threading
from multiprocessing import JoinableQueue, Process, cpu_count
from threading import Thread
from DocuTrace.Utils.Logging import logger, debug, logging
import time


def stream_file_chunks(file_name: str, chunk_size: int=5000000):
    """Use an iterator over the file, using a hint for the number of bytes for each 

    Args:
        file_name (str): Path to the file
        chunk_size (int, optional): The number of bytes each readlines() call will attempt to consume. Defaults to 5000000.

    Yields:
        list(str): A list of strings, each string is one line from the file
    """
    with open(file_name) as f:
        while True:
            data = f.readlines(chunk_size)
            if not data:
                break
            yield data


def stream_read_json(fname: str):
    """Lazy read json generator inspiration for the stream_file_chunks solution (Not used).
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
    """Fast file reading class

    Args:
        path (str, optional): Path to the file. Defaults to None.
        chunk_size (int, optional): The number of bytes each readlines() call will attempt to consume. Defaults to 5000000.
    """

    def __init__(self, path: str=None,  chunk_size: int=5000000):
        if path is not None:
            self.file_iter = stream_file_chunks(path, chunk_size=chunk_size)
        else:
            self.file_iter = None
        self.path = path


    def set_read_path(self, path: str, chunk_size: int=5000000) -> None:
        """Specify the path for LocationViews to read from

        Args:
            path (str): Path to the datafile
            chunk_size (int, optional): The number of bytes each readlines() call will attempt to consume. Defaults to 5000000.
        """
        self.file_iter = stream_file_chunks(path, chunk_size=chunk_size)

    #@debug
    def parse_file(self, data_collector, concurrent: bool=True, max_workers: int=None) -> None:
        """Apply a list of functions to the file_iter

        Args:
            data_collector(DataCollector): A data collection class used to collate all the data.
            concurrent(bool, optional): Enable concurrency when reading. Defaults to True.
            max_workers (int, optional): The max number of workers to process the file input. Defaults to None.


        Raises:
            AttributeError: When a path has not been specified for the file iterator
        """

        if self.file_iter is None:
            raise AttributeError('File iterator not set')

        logger.debug('Begin reading file: {}'.format(self.path))
        if concurrent:
            logger.info('Multiprocessing has been enabled in FileRead.parse_file.')
            with JsonProcessContextManager(data_collector, max_workers) as jtcm:
                for chunk in self.file_iter:
                    jtcm.enqueue(chunk)
                logger.debug('Finished queueing chunks')

        else:
            for chunk in self.file_iter:
                start_time = time.time()
                for line in chunk:
                    try:
                        json_line = line.rstrip()
                        parsed_json = json.loads(json_line)
                        [fn(parsed_json) for fn in data_collector.data_fns]
                    except json.JSONDecodeError as e:
                        logger.exception(
                            'JSON decode error encountered in thread: main. Exception: {}'.format(e))
                duration = time.time() - start_time
                logger.debug('Thread <{}>... one chunk processed. Duration: {} | Chunk size: {}'.format(threading.current_thread(), duration, len(chunk)))

        logger.debug('End reading file: {}'.format(self.path))

class JsonProcessContextManager():
    """Context manager to assist processing large files with processes

        Args:
            data_collector (DataCollector): An instance of the DataCollector class
            max_workers (int): The number of processes to instantiate
        """
    def __init__(self, data_collector, max_workers=None):
        if max_workers is None:
            max_workers = cpu_count()

        self.data_collector = data_collector

        self.queue = JoinableQueue()
        self.feedback_queue = JoinableQueue()
        self.processes = [JsonParseProcess(i, self.data_collector, self.queue, self.feedback_queue) for i in range(max_workers)]
        

    def enqueue(self, chunk: list) -> None:
        """Add a chunk to the queue to be processed by consumer processes

        Args:
            chunk (list(str)): A chunk produced by the stream_file_chunks function
        """
        logger.debug("Enqueuing a chunk | Chunk lines: {}".format(len(chunk)))
        self.queue.put(chunk)

    def __enter__(self):
        logger.debug("Entering context manager")
        [t.start() for t in self.processes]
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if exception_value is not None:
            logger.exception('Exception when leaving context manager: {} | Traceback: {}{'.format(exception_type, traceback))

        retrieve_data = Thread(target=self.retrieve_data, daemon=True)
        retrieve_data.start()

        self.queue.join()
        self.feedback_queue.join()
        logger.debug('Queues flushed')
        
        for process in self.processes:
            process.terminate()

    def retrieve_data(self):
        """Start reading data from feedback queue while waiting for json queue to finish
        """
        while True:
            result = self.feedback_queue.get()
            if result is None:
                break
            self.data_collector.merge(result)
            #self.new_collectors.append(result)
            self.feedback_queue.task_done()
        self.feedback_queue.task_done()


class JsonParseProcess(Process):
    """A process subclass to handle parsing the JSON file

    Args:
        name (Any): A unique identifier for the process
        data_collector (DataCollector): A data collector object that will be written back to after reading is complete
        queue (JoinableQueue): A multiprocessing JoinableQueue, this process will consume elements in the queue
        feedback_queue (JoinableQueue): A multiprocessing JoinableQueue, this process will produce elements for this queue
    """
    def __init__(self, name, data_collector, queue: JoinableQueue, feedback_queue: JoinableQueue):
        super(Process, self).__init__()
        self.t_name = name
        self.data_collector = deepcopy(data_collector)
        self.fn_list = self.data_collector.data_fns
        self.feedback_queue = feedback_queue
        self.queue = queue

    def set_queue(self, queue: JoinableQueue):
        """Assign a reference to the queue to consume from

        Args:
            queue (queue.Queue): A FIFO queue working as a provider for each process

        Returns:
            JsonParseProcess: Self with a queue assigned
        """
        self.queue = queue
        return self

    def run(self) -> None:
        """Begin the process
        """
        logger.debug('Process: {} - running'.format(self.t_name))
        try:
            while True:
                chunk = self.queue.get()
                logger.debug('Process <{}>... Get from queue. | Chunk lines: {}'.format(self.t_name, len(chunk)))

                if chunk is None:
                    logger.debug('PROCESS BREAKING FROM WHILE LOOP')
                    break
                start_time = time.time()

                for line in chunk:
                    try:
                        json_line = line.rstrip()
                        parsed_json = json.loads(json_line)
                        [fn(parsed_json) for fn in self.fn_list]
                    except json.JSONDecodeError as e:
                        logger.exception('JSON decode error encountered in Process: {}. Exception: {}'.format(self.t_name, e))

                to_queue = deepcopy(self.data_collector)
                
                #logger.debug('Putting object on queue with len countries={}. Should have: {}'.format(len(to_queue.countries), len(self.data_collector.countries)))
                self.feedback_queue.put(to_queue)
                self.data_collector.clear()
                
                self.queue.task_done()
                duration = time.time() - start_time
                logger.debug('Process <{}>... one chunk processed. Duration: {} | Chunk lines: {}'.format(self.t_name, duration, len(chunk)))
            
            self.queue.task_done()
            logger.debug('Process <{}>... Terminating'.format(self.t_name))

        finally:
            logger.debug('Process <{}>... IN FINALLY'.format(self.t_name))

