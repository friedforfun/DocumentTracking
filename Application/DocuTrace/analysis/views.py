from .abstractClasses import Analyse

class LocationViews(Analyse):

    def __init__(self, by_country=True):
        self.by_country = by_country
        pass

    def histogram(self):
        pass

    def get_data(self):
        pass


class BrowserViews(Analyse):

    def __init__(self):
        pass

    def histogram(self):
        pass

