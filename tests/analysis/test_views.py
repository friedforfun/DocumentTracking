import pytest
from unittest.mock import patch, mock_open
from DocuTrace.Analysis.DataCollector import DataCollector, ReadingData

mock_file_content = '{"visitor_uuid": "745409913574d4c6", "visitor_country": "MX", "event_readtime": 797, "visitor_useragent":"Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3"}'
json_dict = {
            "visitor_country": "MX",
             "visitor_uuid": "745409913574d4c6",
             "event_readtime": 797,
             "visitor_useragent": "Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3"}


def _setup_Views_class_():
    m = mock_open(read_data=mock_file_content)
    with patch('DocuTrace.analysis.fileRead.open', m) as _file:
        loc_views = DataCollector(path='path')
        _file.assert_not_called()
    return loc_views


def test_count():
    m = mock_open(read_data=mock_file_content)
    with patch('DocuTrace.analysis.fileRead.open', m) as _:
        loc_views = _setup_Views_class_()
        assert loc_views.counted == False
        loc_views.count()
        assert loc_views.counted == True


def test_count_error():
    loc_views = DataCollector()
    with pytest.raises(AttributeError):
        loc_views.count()


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
    assert '745409913574d4c6' not in views.reading_data.keys()
    views.count_read_data(json_dict)
    assert views.reading_data['745409913574d4c6'].read_time == 797

def test_country_name():
    views = DataCollector()
    assert views.country_name('MX') == 'Mexico'


def test_continent_name():
    views = DataCollector()
    assert views.continent_name('MX') == 'North America'


def test_top_reads():
    views = DataCollector()
    views.reading_data = {
        '64bf70296da2f9fd': ReadingData('64bf70296da2f9fd', 500),
        '745409913574d4c6': ReadingData('745409913574d4c6', 1000),
        '9a83c97f415601a6': ReadingData('9a83c97f415601a6', 750)
    }   
    assert views.top_reads(2, False) == {
        '745409913574d4c6': ReadingData('745409913574d4c6', 1000),
        '9a83c97f415601a6': ReadingData('9a83c97f415601a6', 750)
        }
    

def test_sorted():
    views = DataCollector()
    views.countries = {
        'MX': 10,
        'GB': 8,
        'CA': 15
    }
    assert list(views.countries.values()) == [10, 8, 15]
    views.sorted()
    assert list(views.countries.values()) == [15, 10, 8]
    views.sorted(reverse=False)
    assert list(views.countries.values()) == [8, 10, 15]

