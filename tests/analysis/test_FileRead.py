from DocuTrace.Analysis.FileRead import stream_read_json, ParseFile
from DocuTrace.Analysis.DataCollector import DataCollector
import pytest
from unittest.mock import patch, mock_open

key_list = ['visitor_country']

mock_file_content = """{"visitor_country": "MX"}"""

def test_iter_stream_read_json():
    m = mock_open(read_data=mock_file_content)
    with patch('DocuTrace.Analysis.FileRead.open', m) as _file:
        j_iter = stream_read_json('path')
        _file.assert_not_called()
        count = 0
        for i in j_iter:
            count += 1
        _file.assert_called_once_with('path', 'r')
        assert count == 1
    

def test_exception_stream_read_json():
    with patch('DocuTrace.Analysis.FileRead.open',
               new=mock_open(read_data=mock_file_content)) as _file:
        j_iter = stream_read_json('path')
        _file.assert_not_called()
        count = 0
        for i in j_iter:
            count += 1
        _file.assert_called_once_with('path', 'r')
        with pytest.raises(StopIteration):
            next(j_iter)
    

def test_dict_stream_read_json():
    with patch('DocuTrace.Analysis.FileRead.open',
               new=mock_open(read_data=mock_file_content)) as _file:
        j_iter = stream_read_json('path')
        _file.assert_not_called()
        json = next(j_iter)
        _file.assert_called_once_with('path', 'r')
        keys = list(json.keys())
        assert keys == key_list
        assert json.get(key_list[0]) == 'MX'
    

def test_instantiate_ParseFile():
    m = mock_open(read_data=mock_file_content)
    with patch('DocuTrace.Analysis.FileRead.open', m) as _file:
        parser = ParseFile('path')
        _file.assert_not_called()


def test_set_read_path_ParseFile():
    m = mock_open(read_data=mock_file_content)
    with patch('DocuTrace.Analysis.FileRead.open', m) as _file:
        parser = ParseFile('path')
        parser.set_read_path('second_path')
        _file.assert_not_called()


def test_apply_fn_ParseFile():
    m = mock_open(read_data=mock_file_content)
    with patch('DocuTrace.Analysis.FileRead.open', m) as _file:
        parser = ParseFile('path')
        def test_fn1(json):
            assert json.get(key_list[0]) == 'MX'
        def test_fn2(json):
            assert json.get(key_list[0]) == 'MX'
        def test_fn3(json):
            assert json.get(key_list[0]) == 'MX'
        parser.fn_list = [test_fn1, test_fn2, test_fn3]
        parser.parse_file(DataCollector(), threaded=False)


def test_apply_fn_threaded_ParseFile():
    m = mock_open(read_data=mock_file_content)
    with patch('DocuTrace.Analysis.FileRead.open', m) as _file:
        parser = ParseFile('path')

        def test_fn1(json):
            assert json.get(key_list[0]) == 'MX'

        def test_fn2(json):
            assert json.get(key_list[0]) == 'MX'

        def test_fn3(json):
            assert json.get(key_list[0]) == 'MX'
        parser.fn_list = [test_fn1, test_fn2, test_fn3]
        parser.parse_file(DataCollector(), threaded=True)


def test_raise_attributeerr_ParseFile():
        parser = ParseFile()
        def test_fn(json):
            assert json.get(key_list[0]) == 'MX'
        with pytest.raises(AttributeError):
            parser.parse_file(DataCollector(), [test_fn])
