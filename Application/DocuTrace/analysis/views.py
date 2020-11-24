import pycountry
import pycountry_convert
from .abstractClasses import Analyse
from .fileRead import ParseFile
from .plots import Plots

class Views(ParseFile, Analyse):

    def __init__(self, path=None, fig_dimensions=(15, 10)):
        super().__init__(path)
        self.countries = {}
        self.continents = {}
        self.figsize = fig_dimensions
        self.counted = False
        self.histo_config = None

    def count(self):
        self.parse_file([self.count_countries, self.count_continents, self.count_browsers])
        self.counted = True


    def sorted(self, reverse=True):
        """Sort each dict by its values

        Args:
            reverse (bool, optional): Path to the datafile
        """
        self.countries = {k: v for k, v in sorted(
            self.countries.items(), key=lambda item: item[1], reverse=reverse)}
        self.continents = {k: v for k, v in sorted(
            self.continents.items(), key=lambda item: item[1], reverse=reverse)}


    def count_countries(self, json):
        """Increment the dictionary counter for the country in json
        """
        location = json.get('visitor_country', None)
        if location is not None:
            if self.countries.get(location, None) is None:
                self.countries[location] = 1
            else:
                self.countries[location] += 1
        

    def count_continents(self, json):
        """Increment the dictionary counter for the continent derived from the country in json
        """
        location = json.get('visitor_country', None)
        if location is not None:
            continent_name = self.continent_name(location)
            if self.continents.get(continent_name, None) is None:
                self.continents[continent_name] = 1
            else:
                self.continents[continent_name] += 1
        

    def count_browsers(self, json):
        pass


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


    def configure_figure(self, sorted=True, reverse=True, n_continents=None, n_countries=None, show_continents=True, show_countries=True):
        if sorted:
            self.sorted(reverse)
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

        self.histo_config = (data, titles, x_labels, y_labels)
        return (data, titles, x_labels, y_labels)
