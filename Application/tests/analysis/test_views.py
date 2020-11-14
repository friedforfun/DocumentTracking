import pytest
from unittest.mock import patch, mock_open
from Application.DocuTrace.analysis.views import LocationViews, BrowserViews

mock_file_content = """{"visitor_country": "MX"}"""

def _setup_locationviews_class_():
    m = mock_open(read_data=mock_file_content)
    with patch('Application.DocuTrace.analysis.fileRead.open', m) as _file:
        loc_views = LocationViews(path='path')
        _file.assert_not_called()
    return loc_views

def test_count_continents():
    pass

def test_count_countries_error():
    loc_views = LocationViews()
    with pytest.raises(AttributeError):
        loc_views.count_countries()

def test_count_countries():
    m = mock_open(read_data=mock_file_content)
    with patch('Application.DocuTrace.analysis.fileRead.open', m) as _file:
        loc_views = _setup_locationviews_class_()
        loc_views.count_countries()
    assert loc_views.countries == {'MX': 1}

def test_country_name():
    pass

def test_continent_name():
    pass

 # ------------------------------------- BrowserViews ----------------------------------------------
def _setup_browserviews_class_():
    pass
