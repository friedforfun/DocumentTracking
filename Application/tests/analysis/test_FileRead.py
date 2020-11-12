from Application.DocuTrace.analysis.fileRead import stream_read_json
import os
# import pytest

key_list = ['ts', 'visitor_uuid', 'visitor_username', 'visitor_source', 'visitor_device', 'visitor_useragent', 'visitor_ip', 'visitor_country',
 'visitor_referrer', 'env_type', 'env_doc_id', 'env_adid', 'event_type', 'subject_type', 'subject_doc_id', 'subject_page', 'cause_type']

def test_stream_read_json():
    j_iter = stream_read_json(os.path.abspath('./Application/sample_data/issuu_sample.json'))
    json = next(j_iter)
    keys = list(json.keys())
    assert keys == key_list
    assert json.get('visitor_country') == 'MX'

