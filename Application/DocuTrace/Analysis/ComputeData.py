from typing import OrderedDict
import numpy as np
import pycountry
import pycountry_convert
from .Plots import Charts
from DocuTrace.Utils.Exceptions import InvalidDocUUIDError


def sort_dict_by_value(collection: dict, reverse: bool=True) -> list:
    """Sort a dictionary by the values inside, returns a list of keys

    Args:
        collection (dict(str, int)): A dict of string, integer pairs, where the string is the key and the integer is the value
        reverse (bool, optional): reverses the sort, True is descending. Defaults to True.

    Returns:
        list(str): List of strings sorted by the corresponding values from the 'collection' parameter
    """
    return [k for k, _ in sorted(collection.items(), key=lambda item: item[1], reverse=reverse)]


def top_n_sorted(collection: dict, n: int=10) -> list:
    """Get the top n sorted by their values in the dict

    Args:
        collection (dict(str, int)): A dict of string, integer pairs, where the string is the key and the integer is the value
        n (int, optional): Number of values to return. Defaults to 10.

    Returns:
        list(str): List of strings sorted by the corresponding values from the 'collection' parameter
    """
    return sort_dict_by_value(collection, reverse=True)[:n]


def country_name(code: str) -> str:
    """Get the country name from its alpha2 code

    Args:
        code (str): Country code

    Returns:
        str: Country name
    """
    country = pycountry.countries.get(alpha_2=code)
    if country is None:
        return 'Unknown'
    else:
        return country.name


def continent_name(alpha2_country:str) -> str:
    """Get the contenent name from the country

    Args:
        alpha2_country (str): Country code

    Returns:
        str: Continent name
    """          
    try:
        c = pycountry_convert.country_alpha2_to_continent_code(alpha2_country)
        cont = pycountry_convert.convert_continent_code_to_continent_name(c)
    except KeyError:
        return 'Unknown'
    return cont
    
class ComputeData:
    def __init__(self, data_collector, fig_size=(8, 6)):
        self.doc_locations = data_collector.doc_locations
        self.countries = data_collector.countries
        self.continents = data_collector.continents
        self.browser_families = data_collector.browser_families
        self.reader_profiles = data_collector.reader_profiles
        self.document_readers = data_collector.document_readers
        self.visitor_documents = data_collector.visitor_documents
        self.histo_config = None
        self.fig_size = fig_size


    def also_likes_top_10(self, document: str, visitor: str=None) -> list:
        """Get the top 10 also likes for the given parameters

        Args:
            document (str): Document id
            visitor (str, optional): visitor uuid. Defaults to None.

        Returns:
             List(str): A list of the top document ids with 10 elements
        """
        return self.also_likes(document, visitor=visitor, sort_fn=top_n_sorted)


    def also_likes(self, document: str, visitor: str=None, sort_fn=sort_dict_by_value, **kwargs) -> list:
        """For a given document identify which other documents have been read by a reader of this document, when visitor is given exclude them from the resulting list.

        Args:
            document (str): Document id
            visitor (str, optional): visitor uuid. Defaults to None.
            sort_fn (dict(str) -> list(str), optional): A sorting function that takes a dict as its argument and returns a list. Defaults to sort_dict_by_value.

        Returns:
            List(str): A list of document ids, sorted by the provided function
        """
        if document is None or '':
            raise InvalidDocUUIDError('Document ID cannot be None')

        also_likes_dict = self.find_also_likes_counts(document, visitor=visitor)
        return sort_fn(also_likes_dict,  **kwargs)


    def find_also_likes_counts(self, document: str, visitor:str =None) -> dict:
        """Computes also likes based on a document id, and (optionally) a visitor id

        Args:
            document (str): Document id
            visitor (str, optional): visitor uuid. Defaults to None.

        Returns:
            dict(str, int): A dict, where each key is a document id and each key is a count
        """
        relevant_docs, _ = self.find_relevant_docs(document, visitor)
        keys, counts = np.unique(relevant_docs, return_counts=True)
        return dict(zip(keys, counts))


    def find_relevant_docs(self, document: str, visitor: str=None) -> tuple:
        """Finds all documents relevant to the given document, and all readers except the given visitor

        Args:
            document (str): Document id
            visitor (str, optional): visitor uuid. Defaults to None.

        Raises:
            KeyError: Raised when document is not found

        Returns:
            [(numpy.array(str), numpy.array(str))]: [description]
        """
        # key error raised if document not found
        readers = np.array(self.document_readers.get(document))

        # Visitor should be excluded from result
        if visitor in readers:
            readers = readers[readers != visitor]

        docs = []
        for uuid in readers:
            docs += [*self.visitor_documents.get(uuid, '')]

        relevant_docs = np.array(docs)
        relevant_docs = relevant_docs[relevant_docs != '']
        relevant_docs = relevant_docs[relevant_docs != document]
        return relevant_docs, readers


    def sort(self, reverse: bool=True, sort_countries: bool=True, sort_continents: bool=True, sort_browsers: bool=True, sort_reader_profiles: bool=True) -> None:
        """Sort each dict by its values

        Args:
            reverse (bool, optional): Reverse the sorting order, (reverse=True is descending)
            sort_countries (bool, optional): Sort countries in self? Defaults to True.
            sort_continents (bool, optional): Sort continents in self? Defaults to True.
            sort_browsers (bool, optional): Sort browser data in self? Defaults to True.
            sort_reader_profiles (bool, optional): Sort reading data in self? Defaults to True.
        """
        if sort_countries:
            self.countries = {k: v for k, v in sorted(
                self.countries.items(), key=lambda item: item[1], reverse=reverse)}

        if sort_continents:
            self.continents = {k: v for k, v in sorted(
                self.continents.items(), key=lambda item: item[1], reverse=reverse)}

        if sort_browsers:
            self.browser_families = {k: v for k, v in sorted(
                self.browser_families.items(), key=lambda item: item[1], reverse=reverse)}

        if sort_reader_profiles:
            self.reader_profiles = OrderedDict([(k, v) for k, v in sorted(
                self.reader_profiles.items(), key=lambda item: item[1], reverse=reverse)])


    def top_reads(self, top_n=10, to_print=True) -> list:
        """Find the top readers

        Args:
            top_n (int, optional): How many readers to find. Defaults to 10.
            to_print (bool, optional): Print the result? Defaults to True.

        Returns:
            list(ReadingData): A list of top readers
        """
        self.sort(sort_countries=False, sort_continents=False, sort_browsers=False)
        top_readers = dict(list(self.reader_profiles.items())[:top_n])
        if to_print:
            [print(reader) for reader in top_readers]
        return top_readers


    def long_browsers(self) -> dict:
        """Make dict with long browser names as keys

        Returns:
            dict: dict with long browser names as keys
        """
        from DocuTrace.Analysis.DataCollector import merge_dict
        long_browser_names = {}
        for browser in self.browser_families.values():
            long_browser_names = merge_dict(long_browser_names, browser.as_long_name())
        return long_browser_names


    def short_browsers(self) -> dict:
        """Make dict with short browser names as keys

        Returns:
            dict: dict with short browser names as keys
        """
        from DocuTrace.Analysis.DataCollector import merge_dict
        short_browser_names = {}
        for browser in self.browser_families.values():
            short_browser_names = merge_dict(short_browser_names, browser.as_short_name())
        return short_browser_names


    def histogram(self):
        if self.histo_config is not None:
            figure = self.histo_config
        else:
            raise ValueError('histogram construct function must be run first')

        return Charts(n_rows=len(figure[0]), figsize=self.fig_size).histogram(
            figure[0], figure[1], figure[2], figure[3])


    def construct_document_counts_figure(self, doc_uuid, show_countries=True, show_continents=True, sorted=True, reverse=True, n_continents=None, n_countries=None):
        if sorted:
            self.sort(reverse)

        #! Raises KeyError
        doc_data = self.doc_locations.get(doc_uuid, None)
        if doc_data is None:
            raise ValueError('Doc UUID not found')

        continents = doc_data.continents
        countries = doc_data.countries

        if n_continents is not None:
            continents = dict(list(doc_data.continents.items())[:n_continents])

        if n_countries is not None:
            countries = dict(list(doc_data.countries.items())[:n_countries])

        data = []
        titles = []
        x_labels = []
        y_labels = []
        if show_continents:
            data.append(continents)
            titles.append('Document views from each continent')
            x_labels.append('')
            y_labels.append('Continent')

        if show_countries:
            data.append(countries)
            titles.append('Document views from each country')
            x_labels.append('')
            y_labels.append('Country')
        
        self.histo_config = (data, titles, x_labels, y_labels)
        return (data, titles, x_labels, y_labels)


    def construct_counts_figure(self, show_continents=True, show_countries=True, show_browsers=True, sorted=True, reverse=True, n_continents=None, n_countries=None, n_browsers=None, clean_browser_names=True):
        if sorted:
            self.sort(reverse)

        continents = self.continents
        countries = self.countries
        if n_continents is not None:
            continents = dict(list(self.continents.items())[:n_continents])
        if n_countries is not None:
            countries = dict(list(self.countries.items())[:n_countries])
        data = []
        titles = []
        x_labels = []
        y_labels = []
        if show_continents:
            data.append(continents)
            titles.append('Views from each continent')
            x_labels.append('')
            y_labels.append('Continent')

        if show_countries:
            data.append(countries)
            titles.append('Views from each country')
            x_labels.append('')
            y_labels.append('Country')

        if show_browsers:
            if clean_browser_names:
                browsers = self.short_browsers()
            else:
                browsers = self.long_browsers()
            if n_browsers is not None:
                browsers = dict(list(browsers.items())[:n_browsers])

            data.append(browsers)
            titles.append('Views from each browser')
            x_labels.append('')
            y_labels.append('Browser')

        self.histo_config = (data, titles, x_labels, y_labels)
        return (data, titles, x_labels, y_labels)
