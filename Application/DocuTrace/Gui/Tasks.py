import tkinter as tk
from tkinter import ttk

def doc_input(master, doc_stringvar, n_var, btn_fn):
    label = ttk.Label(master, text='Document UUID: ').grid(
        row=0, column=0, padx=10, pady=30)

    input = ttk.Entry(master, textvariable=doc_stringvar)
    input.grid(row=0, column=1, padx=5, pady=30)

    button = ttk.Button(master, text='Go', command=btn_fn)
    button.grid(row=0, column=5, padx=5, pady=30)

    label_n = ttk.Label(master, text='Number to display: ').grid(
        row=0, column=3, padx=10, pady=0)
    input_n = ttk.Entry(master, textvariable=n_var, width=5).grid(
        row=0, column=4, padx=10, pady=0)

    return label, input, button, label_n, input_n


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


def task4d_widgets(tab):
    pass


def task5_widgets(tab):
    pass


def task6_widgets(tab):
    pass
