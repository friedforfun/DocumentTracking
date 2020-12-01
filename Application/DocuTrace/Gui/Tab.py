from tkinter import ttk
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # NavigationToolbar2TkAgg
import matplotlib
matplotlib.use('TkAgg')

from DocuTrace.Utils.Logging import logger
from DocuTrace.Gui.Tasks import *
from DocuTrace.Utils.Validation import check_doc_uuid

tab_dict = {
    'Task 2a': task2a_widgets,
    'Task 2b': task2b_widgets,
    'Task 3a': task3a_widgets,
    'Task 3b': task3b_widgets,
    'Task 4d': task4d_widgets,
    'Task 5': task5_widgets,
    'Task 6': task6_widgets
}


def pass_fn(tab):
    pass


class Tab(ttk.Frame):
    def __init__(self, compute_data, widget_fn=pass_fn, master=None, doc=None, user=None, n=None):
        super().__init__(master)
        self.master = master
        self.compute_data = compute_data
        self.widget_fn = widget_fn
        self.doc_uuid = tk.StringVar(self.master, value=doc)
        self.user_uuid = tk.StringVar(self.master, value=user)
        self.n = tk.IntVar(self.master, value=n)
        self.on_open = None
        widget_fn(self)


    def set_on_open(self, fn):
        self.on_open = fn


    def plot_doc_continents(self):
        n = self.get_n()

        uuid = self.check_uuid()

        self.compute_data.construct_document_counts_figure(
            uuid, show_countries=False, n_continents=n)
        return self.compute_data.histogram()


    def plot_doc_countries(self):
        n = self.get_n()

        uuid = self.check_uuid()

        self.compute_data.construct_document_counts_figure(
            uuid, show_continents=False, n_countries=n)
        return self.compute_data.histogram()


    def plot_browser_counts(self, clean_browser_names=True):
        n = self.get_n()

        self.compute_data.construct_counts_figure(
            show_continents=False, show_countries=False, n_browsers=n, clean_browser_names=clean_browser_names)
        return self.compute_data.histogram()


    def display_chart(self, fig):
        if fig is None:
            logger.warning('Invalid document UUID')
            return

        self.plot_canvas = FigureCanvasTkAgg(fig, self)
        self.plot_canvas.draw()
        self.plot_canvas.get_tk_widget().grid(column=0, row=1, columnspan=6, rowspan=8,  sticky='NSEW')
        self.plot_canvas.get_tk_widget()#.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=40)


    def remove_plot(self):
        try:
            self.plot_canvas.get_tk_widget().destroy()
        except AttributeError as e:
            logger.warning(
                'Attempted to close non-existing or empty canvas. Error: {}'.format(e))


    def doc_elements(self, btn_fn, row=0, inlcude_num=True):
        self.label = ttk.Label(self, text='Document UUID: ').grid(row=row, column=0, padx=15, pady=30)
        self.input = ttk.Entry(self, textvariable=self.doc_uuid).grid(row=row, column=1, padx=10, pady=30)
        self.button = ttk.Button(self, text='Show', command=btn_fn).grid(row=row, column=5, padx=10, pady=30)

        if inlcude_num:
            self.label_n = ttk.Label(self, text='Number to display: ').grid(row=row, column=3, padx=15, pady=0)
            self.input_n = ttk.Entry(self, textvariable=self.n, width=5).grid(row=row, column=4, padx=15, pady=0)


    def n_only(self, btn_fn, row=0):
            self.label_n = ttk.Label(self, text='Number to display: ').grid(row=row, column=0, padx=15, pady=30)
            self.input_n = ttk.Entry(self, textvariable=self.n, width=5).grid(row=row, column=1, padx=15, pady=30)
            self.button = ttk.Button(self, text='Show', command=btn_fn).grid(row=row, column=2, padx=10, pady=30)


    def get_n(self):
        n = self.n.get()
        if n == 0:
            n = None
        return n


    def check_uuid(self):
        uuid = self.doc_uuid.get()
        if not check_doc_uuid(uuid):
            return None
        return uuid
