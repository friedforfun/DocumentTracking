"""Functions to help build relevant gui pages for each task
"""

def task2a_widgets(tab):
    tab.doc_elements(lambda: tab.display_chart(tab.plot_doc_countries()))
    tab.set_on_open(lambda: tab.display_chart(tab.plot_doc_countries()))


def task2b_widgets(tab):
    tab.doc_elements(lambda: tab.display_chart(tab.plot_doc_continents()))
    tab.set_on_open(lambda: tab.display_chart(tab.plot_doc_continents()))


def task3a_widgets(tab):
    tab.n_only(lambda: tab.display_chart(tab.plot_browser_counts(False)))
    tab.set_on_open(lambda: tab.display_chart(tab.plot_browser_counts(False)))


def task3b_widgets(tab):
    tab.n_only(lambda: tab.display_chart(tab.plot_browser_counts(True)))
    tab.set_on_open(lambda: tab.display_chart(tab.plot_browser_counts(True)))


def task4_widgets(tab):
    tab.n_only(tab.display_reader_profiles)
    tab.set_on_open(tab.display_reader_profiles)

def task5d_widgets(tab):
    tab.doc_elements(tab.display_also_likes_text)
    tab.user_elements(row=1)
    tab.set_on_open(tab.display_also_likes_text)


def task6_widgets(tab):
    tab.doc_elements(tab.display_also_likes_graph)
    tab.user_elements(row=1)
    tab.set_on_open(tab.display_also_likes_graph)
