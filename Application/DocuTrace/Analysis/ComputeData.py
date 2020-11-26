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
    def __init__(self, document_readers, visitor_documents):
        self.document_readers = document_readers
        self.visitor_documents = visitor_documents

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



