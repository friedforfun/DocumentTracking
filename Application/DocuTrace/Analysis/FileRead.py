import json
from DocuTrace.Utils.Logging import logger
import threading

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

    def parse_file(self, fn_list, threaded=True):
        """Apply a list of functions to the file_iter

        Args:
            fn_list (list(dict->None)): A list of functions that all take a dict as a parameter
        """
        if self.file_iter is None:
            raise AttributeError('File iterator not set')
        logger.debug('Begin reading file: {}'.format(self.path))
        # Possible threading opportunity here
        if threaded:
            threads = [JsonParseThread(i, f) for i, f in enumerate(fn_list)]
        for json in self.file_iter:
            if threaded:
                [t.start() for t in threads]
                [t.join() for t in threads]
            else:
                [fn(json) for fn in fn_list]
        logger.info('End reading file: {}'.format(self.path))


class JsonParseThread(threading.Thread):
    def __init__(self, name, fn):
        threading.Thread.__init__(self)
        self.name = name
        self.fn = fn

    def run(self, json):
        logger.debug('Thread: {} - running'.format(self.name))
        self.fn(json)
