import pytest
from unittest.mock import patch, mock_open
from DocuTrace.analysis.views import Views

mock_file_content = '{"visitor_country": "MX", "visitor_useragent":"Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3"}'
json_dict = {"visitor_country": "MX",
             "visitor_useragent": "Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3"}


def _setup_Views_class_():
    m = mock_open(read_data=mock_file_content)
    with patch('DocuTrace.analysis.fileRead.open', m) as _file:
        loc_views = Views(path='path')
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
    loc_views = Views()
    with pytest.raises(AttributeError):
        loc_views.count()


def test_count_countries():
    views = Views()
    assert 'MX' not in views.countries.keys()
    views.count_countries(json_dict)
    assert views.countries['MX'] == 1


def test_count_continents():
    views = Views()
    assert 'North America' not in views.continents.keys()
    views.count_continents(json_dict)
    assert views.continents['North America'] == 1

def test_count_browsers():
    views = Views()
    assert 'Mobile Safari' not in views.browser_families.keys()
    views.count_browsers(json_dict)
    assert views.browser_families['Mobile Safari'] == 1


def test_country_name():
    views = Views()
    assert views.country_name('MX') == 'Mexico'


def test_continent_name():
    views = Views()
    assert views.continent_name('MX') == 'North America'


def test_sorted():
    views = Views()
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

