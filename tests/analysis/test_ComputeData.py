from DocuTrace.Analysis.ComputeData import ComputeData, sort_dict_by_value, top_n_sorted, country_name, continent_name
from DocuTrace.Analysis.DataCollector import ReadingData, DataCollector

dc = DataCollector()
dc.countries = {
    'MX': 1
}

dc.continents = {
    'North America': 1
}

dc.browser_families = {
    'Firefox': 1
}

dc.reader_profiles = {
    '64bf70296da2f9fd': ReadingData('64bf70296da2f9fd', 500),
    '745409913574d4c6': ReadingData('745409913574d4c6', 1000),
    '9a83c97f415601a6': ReadingData('9a83c97f415601a6', 750)
}

dc.document_readers = {
    '123': ['a'],
    '456': ['a', 'b'],
    '789': ['b', 'c']
}

dc.visitor_documents = {
    'a': ['123', '456'],
    'b': ['456', '789'],
    'c': '789'
}

countries = {
    'MX': 10,
    'GB': 8,
    'CA': 15
}

dict_of_counts = {
    '123': 3,
    '456': 5,
    '789': 1
}

def test_sort_dict_by_value():
    assert sort_dict_by_value(dict_of_counts) == ['456', '123', '789']

def test_sort_dict_by_value_reversed():
    assert sort_dict_by_value(dict_of_counts, reverse=False) == ['789', '123', '456']

def test_sort_dict_by_value_empty():
    assert sort_dict_by_value({}) == []


def test_top_n_sorted():
    test_dict = {v: k for k, v in enumerate(map(str, list(range(20))))}
    sorted_list = top_n_sorted(test_dict)
    assert sorted_list == list(map(str, reversed(range(10, 20))))
    assert len(sorted_list) == 10

def test_top_n_sorted_empty():
    assert top_n_sorted({}) == []


def test_country_name():
    assert country_name('MX') == 'Mexico'


def test_continent_name():
    assert continent_name('MX') == 'North America'


def test_find_also_likes_no_visitor():
    compute = ComputeData(dc)
    assert compute.find_also_likes_counts('456') == {'123': 1, '789': 1}
    assert dc.document_readers == {
        '123': ['a'],
        '456': ['a', 'b'],
        '789': ['b', 'c']
    }


def test_find_also_likes_counts_visitor():
    compute = ComputeData(dc)
    assert compute.find_also_likes_counts('456', 'a') == {'789': 1}
    # document_readers was getting mutated
    assert dc.document_readers == {
        '123': ['a'],
        '456': ['a', 'b'],
        '789': ['b', 'c']
    }

def test_also_likes_no_visitor():
    compute = ComputeData(dc)
    assert compute.also_likes('456', visitor=None) == ['123', '789']

def test_also_likes_visitor():
    compute = ComputeData(dc)
    assert compute.also_likes('456', 'a') == ['789']


def test_also_likes_top_10():
    pass


def test_sort():
    compute = ComputeData(dc)
    compute.countries = countries
    assert list(compute.countries.values()) == [10, 8, 15]
    compute.sort(reverse=True)
    assert list(compute.countries.values()) == [15, 10, 8]
    compute.sort(reverse=False)
    assert list(compute.countries.values()) == [8, 10, 15]


def test_top_reads():
    compute = ComputeData(dc)
    assert compute.top_reads(2, False) == {
        '745409913574d4c6': ReadingData('745409913574d4c6', 1000),
        '9a83c97f415601a6': ReadingData('9a83c97f415601a6', 750)
    }
