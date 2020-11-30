import pytest
from unittest.mock import patch, mock_open
from DocuTrace.Analysis.DataCollector import DataCollector, ReadingData

mock_file_content = '{"visitor_uuid": "745409913574d4c6", "env_doc_id": "130705172251-3a2a725b2bbd5aa3f2af810acf0aeabb", "visitor_country": "MX", "event_readtime": 797, "visitor_useragent":"Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3"}'
json_dict = {
            "visitor_country": "MX",
             "visitor_uuid": "745409913574d4c6",
             "subject_doc_id": "130705172251-3a2a725b2bbd5aa3f2af810acf0aeabb",
             "event_readtime": 797,
             "visitor_useragent": "Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3"}


def _setup_Views_class_():
    m = mock_open(read_data=mock_file_content)
    with patch('DocuTrace.Analysis.FileRead.open', m) as _file:
        loc_views = DataCollector(path='path')
        _file.assert_not_called()
    return loc_views


def test_count():
    m = mock_open(read_data=mock_file_content)
    with patch('DocuTrace.Analysis.FileRead.open', m) as _:
        loc_views = _setup_Views_class_()
        assert loc_views.counted == False
        loc_views.gather_data()
        assert loc_views.counted == True


def test_count_error():
    loc_views = DataCollector()
    with pytest.raises(AttributeError):
        loc_views.gather_data()


def test_count_countries():
    views = DataCollector()
    assert 'MX' not in views.countries.keys()
    views.count_countries(json_dict)
    assert views.countries['MX'] == 1


def test_count_continents():
    views = DataCollector()
    assert 'North America' not in views.continents.keys()
    views.count_continents(json_dict)
    assert views.continents['North America'] == 1

def test_count_browsers():
    views = DataCollector()
    assert 'Mobile Safari' not in views.browser_families.keys()
    views.count_browsers(json_dict)
    assert views.browser_families['Mobile Safari'] == 1

def test_count_user_reads():
    views = DataCollector()
    assert '745409913574d4c6' not in views.reader_profiles.keys()
    views.collect_reading_data(json_dict)
    assert views.reader_profiles['745409913574d4c6'].read_time == 797


def test_collect_document_readers():
    views = DataCollector()
    assert '130705172251-3a2a725b2bbd5aa3f2af810acf0aeabb' not in views.document_readers.keys()
    assert '745409913574d4c6' not in views.visitor_documents.keys()
    views.collect_document_readers(json_dict)
    assert views.document_readers['130705172251-3a2a725b2bbd5aa3f2af810acf0aeabb'] == ['745409913574d4c6']
    assert views.visitor_documents['745409913574d4c6'] == ['130705172251-3a2a725b2bbd5aa3f2af810acf0aeabb']
