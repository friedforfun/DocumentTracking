import pycountry
import pycountry_convert
from .abstractClasses import Analyse
from .fileRead import stream_read_json
from matplotlib import pyplot as plt

class LocationViews(Analyse):

    def __init__(self, fig_dimensions=(14, 12)):
        self.countries = {}
        self.continents = {}
        self.figsize = fig_dimensions

    def histogram(self):
        ax1 = self.continents_ax()
        ax2 = self.countries_ax()
        plt.show()

    def countries_ax(self):
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
        fig, ax = plt.subplots(figsize=self.figsize)
        x_ticks = ['']
        for i, (k, v) in enumerate(self.continents.items()):
            ax.bar(i, v, label=k)
            x_ticks.append(k)
        ax.set_title('Views from each continent')
        ax.set_ylabel('Number of views')
        ax.set_xticklabels(x_ticks, rotation=45)
        #ax.legend()
        print(x_ticks)
        return ax

    def count_countries(self, path):
        """Load and count the data

        Args:
            path (str): Path to the datafile
        """
        j_iter = stream_read_json(path)
        self.countries = {}
        for json in j_iter:
            location = json.get('visitor_country', None)
            if location is not None:
                current = self.countries.get(location)
                if current is None:
                    self.countries[location] = 0
                self.countries[location] += 1


    def count_continents(self):
        """Calculate the values for the number of viewers per continent
        """
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

