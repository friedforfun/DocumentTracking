import json

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


