from DocuTrace.Analysis.ComputeData import ComputeData, sort_dict_by_value, top_n_sorted, country_name, continent_name

document_readers = {
    '123': ['a'],
    '456': ['a', 'b'],
    '789': ['b', 'c']
}

visitor_documents = {
    'a': ['123', '456'],
    'b': ['456', '789'],
    'c': '789'
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
    compute = ComputeData(document_readers, visitor_documents)
    assert compute.find_also_likes('456') == {'123': 1, '789': 1}
    assert document_readers == {
        '123': ['a'],
        '456': ['a', 'b'],
        '789': ['b', 'c']
    }


def test_find_also_likes_visitor():
    compute = ComputeData(document_readers, visitor_documents)
    assert compute.find_also_likes('456', 'a') == {'789': 1}
    # document_readers was getting mutated
    assert document_readers == {
        '123': ['a'],
        '456': ['a', 'b'],
        '789': ['b', 'c']
    }

def test_also_likes_no_visitor():
    compute = ComputeData(document_readers, visitor_documents)
    assert compute.also_likes('456', visitor=None) == ['123', '789']

def test_also_likes_visitor():
    compute = ComputeData(document_readers, visitor_documents)
    assert compute.also_likes('456', 'a') == ['789']


def test_also_likes_top_10():
    pass
