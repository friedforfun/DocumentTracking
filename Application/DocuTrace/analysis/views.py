import pycountry
import pycountry_convert
from .abstractClasses import Analyse
from .fileRead import stream_read_json
from matplotlib import pyplot as plt

class LocationViews(Analyse):

    def __init__(self, path=None, fig_dimensions=(14, 12)):
        if path is not None:
            self.file_iter = stream_read_json(path)
        else:
            self.file_iter = None
        self.countries = {}
        self.continents = {}
        self.figsize = fig_dimensions
        self.counted = False

    def set_read_path(self, path):
        """Specify the path for LocationViews to read from

        Args:
            path (str): Path to the datafile
        """
        self.file_iter = stream_read_json(path)
        self.counted = False

    def histogram(self):
        ax1 = self.continents_ax()
        ax2 = self.countries_ax()
        plt.show()

    def countries_ax(self):
        if not self.counted:
            self.count_countries()
        fig, ax = plt.subplots(figsize=self.figsize)
        x_ticks = []
        for i, (k, v) in enumerate(self.countries.items()):
            ax.bar(i, v, label=k)
            x_ticks.append(self.country_name(k))
        ax.set_title('Views from each country')
        ax.set_ylabel('Number of views')
        ax.set_xticklabels(x_ticks, rotation=45)
        #ax.legend()

        return ax

    def continents_ax(self):
        if not self.counted or self.continents is {}:
            self.count_continents()
        fig, ax = plt.subplots(figsize=self.figsize)
        x_ticks = ['']
        for i, (k, v) in enumerate(self.continents.items()):
            ax.bar(i, v, label=k)
            x_ticks.append(k)
        ax.set_title('Views from each continent')
        ax.set_ylabel('Number of views')
        ax.set_xticklabels(x_ticks, rotation=45)
        #ax.legend()
        return ax

    def count_countries(self):
        """Count the number of occurences of each country
        """
        if self.file_iter is None:
            raise AttributeError('File iterator not set')
        self.countries = {}
        for json in self.file_iter:
            location = json.get('visitor_country', None)
            if location is not None:
                current = self.countries.get(location)
                if current is None:
                    self.countries[location] = 0
                self.countries[location] += 1
        self.counted = True


    def count_continents(self):
        """Count the number of occurences of each continent
        """
        if not self.counted:
            self.count_countries
        for code in self.countries:
            name = self.continent_name(code)
            current = self.continents.get(name)
            if current is None:
                self.continents[name] = 0
            self.continents[name] += self.countries.get(code)

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


class BrowserViews(Analyse):

    def __init__(self):
        pass

    def histogram(self):
        pass

