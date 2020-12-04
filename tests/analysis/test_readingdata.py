from DocuTrace.Analysis.DataCollector import ReadingData


def test_constructor():
    read_data = ReadingData('test')
    assert read_data.reads == 1

def test_rew_read():
    read_data = ReadingData('test')
    assert read_data.reads == 1
    read_data.new_read(600)
    assert read_data.reads == 2
    assert read_data.read_time == 600

def test_is_valid_operand():
    read_data = ReadingData('test')
    assert read_data.is_valid_operand(20)
    assert read_data.is_valid_operand(ReadingData('test2'))
    assert not read_data.is_valid_operand(0.1)


def test_total_ordering():
    read_data = ReadingData('test')
    assert read_data == 0
    assert read_data < 10
    assert read_data != 1
    read_data.new_read(500)
    assert read_data > 10
    assert read_data == 500
    assert read_data >= 500
    assert read_data <= 500
    read_data2 = ReadingData('test2')
    assert not read_data == read_data2
    read_data2.new_read(500)
    assert read_data == read_data2

