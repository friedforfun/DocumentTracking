from functools import total_ordering
from user_agents import parse as ua_parse

from .AbstractClasses import Analyse
from .FileRead import ParseFile
from ..Utils.Logging import logger

from .ComputeData import continent_name


def merge_dict(own: dict, other: dict) -> dict:
    """Merge other dict with self

    Args:
        own (dict): the dict being merged into
        other (dict): the dict being read from
    """
    for element in other:
        if own.get(element, None) is None:
            own[element] = other[element]
        else:
            own[element] += other[element]
    return own

@total_ordering
class ReadingData:
    """Stores user uuid, reading time and number of reads. Implements comparison, addition, and printing operators.

    Args:
        uuid (str): User uuid
        read_time (int, optional): Amount of read time to initialise this user wtih. Defaults to 0.
        reads (int, optional): Number times this user has read a document. Defaults to 1.
    """
    def __init__(self, uuid, read_time=0, reads=1):
        self.uuid = uuid
        self.read_time = read_time
        self.reads = reads

    def new_read(self, read_time: int) -> None:
        """Used to update the total reading time of this user.

        Args:
            read_time (int): Read time from a document
        """
        self.read_time += read_time
        self.reads += 1

    def _is_valid_operand(self, other) -> bool:
        return(hasattr(other, "read_time") or type(other) == int)

    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        if type(other) == int:
            return self.read_time == other
        else:
            return self.read_time == other.read_time

    def __lt__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        if type(other) == int:
            return self.read_time < other
        else:
            return self.read_time < other.read_time

    def __repr__(self):
        return "ReadingData(uuid:{}, Read time:{}, Number of reads:{})".format(self.uuid, self.read_time, self.reads)

    def __str__(self):
        return "<uuid:{}, Read time:{}, Number of reads:{}>".format(self.uuid, self.read_time, self.reads)

    def __add__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented

        if self.uuid != other.uuid:
            return NotImplemented

        total_read_time = self.read_time + other.read_time
        total_reads = self.reads + other.reads
        return ReadingData(self.uuid, total_read_time, total_reads)


class DataCollector:
    """Handles collection and orgnaisation of data

    Args:
        path (str, optional): Path to the file being read. Defaults to None.
        count_browser (bool, optional): Count browser data? Defaults to True.
        count_country (bool, optional): Count country data? Defaults to True.
        count_continent (bool, optional): Count continent data? Defaults to True.
        build_reader_profiles (bool, optional): Build reader profiles? Defaults to True.
        collect_doc_data (bool, optional): Collect document-reader relationships? Defaults to True.
    """
    def __init__(self, path: str=None, count_browser: bool=True, count_country: bool=True, count_continent: bool=True, build_reader_profiles: bool=True, collect_doc_data: bool=True):
        self.path = path
        self.countries = {}
        self.continents = {}
        self.browser_families = {}
        self.reader_profiles = {}
        self.document_readers = {}
        self.visitor_documents = {}
        self.counted = False
        self.histo_config = None

        self.data_fns = []
        if count_browser:
            self.data_fns.append(self.count_browsers)
        if count_country:
            self.data_fns.append(self.count_countries)
        if count_continent:
            self.data_fns.append(self.count_continents)
        if build_reader_profiles:
            self.data_fns.append(self.collect_reading_data)
        if collect_doc_data:
            self.data_fns.append(self.collect_document_readers)

    def set_read_path(self, path: str) -> None:
        """Specify the path for LocationViews to read from

        Args:
            path (str): Path to the datafile
        """
        self.path = path

    def gather_data(self, concurrent: bool=True, max_workers: int=None, chunk_size: int=500000) -> None:
        """Compute the counts of the required data
        """
        ParseFile(self.path, chunk_size=chunk_size).parse_file(
            self, concurrent=concurrent, max_workers=max_workers)
        self.counted = True


    def count_countries(self, json: dict) -> None:
        """Increment the dictionary counter for the country in json

        Args:
            json (dict): dict returned by json.load
        """
        location = json.get('visitor_country', None)
        if location is not None:
            if self.countries.get(location, None) is None:
                self.countries[location] = 1
            else:
                self.countries[location] += 1
        

    def count_continents(self, json: dict) -> None:
        """Increment the dictionary counter for the continent derived from the country in json

        Args:
            json (dict): dict returned by json.load
        """
        location = json.get('visitor_country', None)
        if location is not None:
            continent_n = continent_name(location)
            if self.continents.get(continent_n, None) is None:
                self.continents[continent_n] = 1
            else:
                self.continents[continent_n] += 1
        

    def count_browsers(self, json: dict) -> None:
        """Update the browser family count field in self

        Args:
            json (dict): dict returned by json.load
        """
        ua_string = json.get('visitor_useragent', None)
        if ua_string is not None:
            user_agent = ua_parse(ua_string)
            browser = user_agent.browser.family
            if self.browser_families.get(browser, None) is None:
                self.browser_families[browser] = 1
            else:
                self.browser_families[browser] += 1


    def collect_reading_data(self, json: dict) -> None:
        """Update reading data for each uuid

        Args:
            json (dict): dict returned by json.load
        """
        reading_time = json.get('event_readtime')
        uuid = json.get('visitor_uuid')
        if reading_time is not None and uuid is not None:
            if self.reader_profiles.get(uuid, None) is None:
                self.reader_profiles[uuid] = ReadingData(uuid, read_time=reading_time)
            else:
                self.reader_profiles[uuid].new_read(reading_time)


    def collect_document_readers(self, json: dict) -> None:
        """Collect document id and reader id information

        Args:
            json (dict): dict returned by json.load
        """
        document = json.get('env_doc_id')
        uuid = json.get('visitor_uuid')
        if document is not None and uuid is not None:
            if self.document_readers.get(document, None) is None:
                self.document_readers[document] = [uuid]
            else:
                self.document_readers[document].append(uuid)
            if self.visitor_documents.get(uuid, None) is None:
                self.visitor_documents[uuid] = [document]
            else:
                self.visitor_documents[uuid].append(document)


    def merge(self, other) -> None:
        """Merge the dictionaries of other with self

        Args:
            other (DataCollector): other must be a DataCollector instance
        """
        self.countries = merge_dict(self.countries, other.countries)
        self.continents = merge_dict(self.continents, other.continents)
        self.browser_families = merge_dict(self.browser_families, other.browser_families)
        self.reader_profiles = merge_dict(self.reader_profiles, other.reader_profiles)
        self.document_readers = merge_dict(self.document_readers, other.document_readers)
        self.visitor_documents = merge_dict(self.visitor_documents, other.visitor_documents)

    def clear(self) -> None:
        self.countries = {}
        self.continents = {}
        self.browser_families = {}
        self.reader_profiles = {}
        self.document_readers = {}
        self.visitor_documents = {}


#! --------------------- MOVE TO NEW CLASS -------------------------


