from functools import total_ordering
import pycountry
import pycountry_convert
from user_agents import parse as ua_parse
from .AbstractClasses import Analyse
from .FileRead import ParseFile
from .Plots import Plots

@total_ordering
class ReadingData:
    """Stores user uuid, reading time and number of reads.

    Args:
        uuid (str): User uuid
        read_time (int, optional): Amount of read time to initialise this user wtih. Defaults to 0.
        reads (int, optional): Number times this user has read a document. Defaults to 1.
    """
    def __init__(self, uuid, read_time=0, reads=1):
        self.uuid = uuid
        self.read_time = read_time
        self.reads = reads

    def new_read(self, read_time):
        """Used to update the total reading time of this user.

        Args:
            read_time (int): Read time from a document
        """
        self.read_time += read_time
        self.reads += 1

    def _is_valid_operand(self, other):
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
        return "ReadingData(uuid:%s, Read time:%s, Number of reads:%s)" % (self.uuid, self.read_time, self.reads)

    def __str__(self):
        return "<uuid:%s, Read time:%s, Number of reads:%s>\n" % (self.uuid, self.read_time, self.reads)

class DataCollector(ParseFile, Analyse):

    def __init__(self, path=None, fig_dimensions=(15, 10), count_browser=True, count_country=True, count_continent=True, count_reads=True):
        super().__init__(path)
        self.countries = {}
        self.continents = {}
        self.browser_families = {}
        self.reading_data = {}
        self.figsize = fig_dimensions
        self.counted = False
        self.histo_config = None

        self.count_fns = []
        if count_browser:
            self.count_fns.append(self.count_browsers)
        if count_country:
            self.count_fns.append(self.count_countries)
        if count_continent:
            self.count_fns.append(self.count_continents)
        if count_reads:
            self.count_fns.append(self.count_read_data)


    def count(self):
        """Compute the counts of the required data
        """
        self.parse_file(self.count_fns)
        self.counted = True


    def sorted(self, reverse=True, sort_countries=True, sort_continents=True, sort_browsers=True, sort_reading_data=True):
        """Sort each dict by its values

        Args:
            reverse (bool, optional): Reverse the sorting order, (reverse=True is descending)
            sort_countries (bool, optional): Sort countries in self? Defaults to True.
            sort_continents (bool, optional): Sort continents in self? Defaults to True.
            sort_browsers (bool, optional): Sort browser data in self? Defaults to True.
            sort_reading_data (bool, optional): Sort reading data in self? Defaults to True.
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

        if sort_reading_data:
            self.reading_data = {k: v for k, v in sorted(
                self.reading_data.items(), key=lambda item: item[1], reverse=reverse)}


    def count_countries(self, json):
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
        

    def count_continents(self, json):
        """Increment the dictionary counter for the continent derived from the country in json

        Args:
            json (dict): dict returned by json.load
        """
        location = json.get('visitor_country', None)
        if location is not None:
            continent_name = self.continent_name(location)
            if self.continents.get(continent_name, None) is None:
                self.continents[continent_name] = 1
            else:
                self.continents[continent_name] += 1
        

    def count_browsers(self, json):
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


    def count_read_data(self, json):
        """Update reading data for each uuid

        Args:
            json (dict): dict returned by json.load
        """
        reading_time = json.get('event_readtime')
        uuid = json.get('visitor_uuid')
        if reading_time is not None and uuid is not None:
            if self.reading_data.get(uuid, None) is None:
                self.reading_data[uuid] = ReadingData(uuid, read_time=reading_time)
            else:
                self.reading_data[uuid].new_read(reading_time)
        elif reading_time is None and uuid is not None:
            if self.reading_data.get(uuid, None):
                self.reading_data[uuid] = ReadingData(uuid, read_time=0, reads=0)


    def top_reads(self, top_n=10, to_print=True):
        """Find the top readers

        Args:
            top_n (int, optional): How many readers to find. Defaults to 10.
            to_print (bool, optional): Print the result? Defaults to True.

        Returns:
            list(ReadingData): A list of top readers
        """
        self.sorted(sort_countries=False, sort_continents=False, sort_browsers=False)
        top_readers = dict(list(self.reading_data.items())[:top_n])
        if to_print:
            [print(reader) for reader in top_readers]
        return top_readers

    def country_name(self, code):
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


    def continent_name(self, alpha2_country):
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


    def histogram(self):
        if self.histo_config is not None:
            figure = self.histo_config
        else:
            figure = self.configure_figure()
        Plots(n_rows=len(figure[0]), figsize=self.figsize).histogram(
            figure[0], figure[1], figure[2], figure[3])

    def configure_figure(self, show_continents=True, show_countries=True, show_browsers=True, sorted=True, reverse=True, n_continents=None, n_countries=None, n_browsers=None):
        if sorted:
            self.sorted(reverse)
        
        continents = self.continents
        countries = self.countries
        browsers = self.browser_families
        if n_continents is not None:
            continents = dict(list(self.continents.items())[:n_continents])
        if n_countries is not None:
            countries = dict(list(self.countries.items())[:n_countries])
        if n_browsers is not None:
            browsers = dict(list(self.browser_families.items())[:n_browsers])
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
            data.append(browsers)
            titles.append('Views from each browser')
            x_labels.append('')
            y_labels.append('Browser')

        self.histo_config = (data, titles, x_labels, y_labels)
        return (data, titles, x_labels, y_labels)

