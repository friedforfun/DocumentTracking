import numpy as np
from copy import deepcopy
import pycountry
import pycountry_convert

def sort_dict_by_value(collection, reverse=True):
    """Sort a dictionary by the values inside, returns a list of keys

    Args:
        collection (dict(str, int)): A dict of string, integer pairs, where the string is the key and the integer is the value
        reverse (bool, optional): reverses the sort, True is descending. Defaults to True.

    Returns:
        list(str): List of strings sorted by the corresponding values from the 'collection' parameter
    """
    return [k for k, _ in sorted(collection.items(), key=lambda item: item[1], reverse=reverse)]


def top_n_sorted(collection, n=10):
    """Get the top n sorted by their values in the dict

    Args:
        collection (dict(str, int)): A dict of string, integer pairs, where the string is the key and the integer is the value
        n (int, optional): Number of values to return. Defaults to 10.

    Returns:
        list(str): List of strings sorted by the corresponding values from the 'collection' parameter
    """
    return sort_dict_by_value(collection, reverse=True)[:n]


def country_name(code):
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


def continent_name(alpha2_country):
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
    def __init__(self, data_collector):
        self.countries = data_collector.countries
        self.continents = data_collector.continents
        self.browser_families = data_collector.browser_families
        self.reader_profiles = data_collector.reader_profiles
        self.document_readers = data_collector.document_readers
        self.visitor_documents = data_collector.visitor_documents

    def also_likes_top_10(self, document, visitor=None):
        """Get the top 10 also likes for the given parameters

        Args:
            document (str): Document id
            visitor (str, optional): visitor uuid. Defaults to None.

        Returns:
             List(str): A list of the top document ids with 10 elements
        """
        return self.also_likes(document, visitor=visitor, sort_fn=top_n_sorted)


    def also_likes(self, document, visitor=None, sort_fn=sort_dict_by_value):
        """For a given document identify which other documents have been read by this document, when visitor is given exclude them from the resulting list.

        Args:
            document (str): Document id
            visitor (str, optional): visitor uuid. Defaults to None.
            sort_fn (dict(str, int) -> list(str), optional): A sorting function that takes a dict as its argument and returns a list. Defaults to sort_dict_by_value.

        Returns:
            List(str): A list of document ids, sorted by the provided function
        """
        print(self.document_readers)
        print(self.visitor_documents)
        also_likes_dict = self.find_also_likes(document, visitor=visitor)
        print(also_likes_dict)
        return sort_fn(also_likes_dict)


    def find_also_likes(self, document, visitor=None):
        """Computes also likes based on a document id, and (optionally) a visitor id

        Args:
            document (str): Document id
            visitor (str, optional): visitor uuid. Defaults to None.

        Returns:
            dict(str, int): A dict, where each key is a document id and each key is a count
        """
        # key error raised if document not found
        # deep copy to prevent mutating self.document_readers
        readers = deepcopy(self.document_readers.get(document))

        # Visitor should be excluded from result
        if visitor in readers:
            readers.remove(visitor)

        relevant_docs = np.array([self.visitor_documents.get(uuid, ['']) for uuid in readers], dtype=object).flatten()
        relevant_docs = relevant_docs[relevant_docs != '']
        relevant_docs = relevant_docs[relevant_docs != document]

        keys, counts = np.unique(relevant_docs, return_counts=True)
        return dict(zip(keys, counts))


    def sort(self, reverse=True, sort_countries=True, sort_continents=True, sort_browsers=True, sort_reader_profiles=True):
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
            self.reader_profiles = {k: v for k, v in sorted(
                self.reader_profiles.items(), key=lambda item: item[1], reverse=reverse)}


    def top_reads(self, top_n=10, to_print=True):
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

