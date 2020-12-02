from tkinter import ttk
import tkinter as tk
import os
from PIL import ImageTk, Image
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # NavigationToolbar2TkAgg

from DocuTrace.Analysis.ComputeData import top_n_sorted
from DocuTrace.Analysis.Plots import Graphs
from DocuTrace.Utils.Logging import debug, logger
from DocuTrace.Gui.Tasks import *
from DocuTrace.Utils.Validation import check_doc_uuid, check_user_uuid


tab_dict = {
    'Task 2a': task2a_widgets,
    'Task 2b': task2b_widgets,
    'Task 3a': task3a_widgets,
    'Task 3b': task3b_widgets,
    'Task 4': task4_widgets,
    'Task 5d': task5d_widgets,
    'Task 6': task6_widgets
}


def pass_fn(tab) -> None:
    """Convienence function for instantiating Tabs, does nothing

    Args:
        tab (Any): Dummy param
    """
    pass

class Controls(ttk.Frame):
    def __init__(self, parent, doc_uuid, user_uuid, n):
        super().__init__(parent, borderwidth=5, relief="sunken", width=500, height=80)
        self.doc_uuid = doc_uuid
        self.user_uuid = user_uuid
        self.n = n
        logger.info('Info constructor')

    def doc_elements(self, btn_fn, row: int=1, inlcude_num: bool=True) -> None:
        """Create the elements for doc uuid input and possibly number to display.

        Args:
            btn_fn (Any -> Any): Function to run on button press
            row (int, optional): The row to place these gui elements. Defaults to 0.
            inlcude_num (bool, optional): Inlcude the n input fields. Defaults to True.
        """
        self.label = ttk.Label(self, text='Document UUID: ').grid(row=row, column=0, padx=15, pady=5)
        self.input = ttk.Entry(self, textvariable=self.doc_uuid).grid(row=row, column=1, padx=10, pady=5)
        self.button = ttk.Button(self, text='Show', command=btn_fn).grid(row=row, column=4, padx=10, pady=5)

        if inlcude_num:
            self.label_n = ttk.Label(self, text='Number to display: ').grid(row=row, column=2, padx=15, pady=5)
            self.input_n = ttk.Entry(self, textvariable=self.n, width=5).grid(row=row, column=3, padx=15, pady=5)


    def n_only(self, btn_fn, row: int=1) -> None:
        """Create gui elements for number to display input fields, used when no doc uuid is needed

        Args:
            btn_fn (Any -> Any): Function to run on button press
            row (int, optional): Row to place gui elements on. Defaults to 0.
        """
        self.label_n = ttk.Label(self, text='Number to display: ').grid(row=row, column=0, padx=15, pady=5)
        self.input_n = ttk.Entry(self, textvariable=self.n, width=5).grid(row=row, column=1, padx=15, pady=5)
        self.button = ttk.Button(self, text='Show', command=btn_fn).grid(row=row, column=2, padx=10, pady=5)


    def user_elements(self, row: int=1) -> None:
        """Create user uuid gui input elements

        Args:
            row (int, optional): The row to place these elements on. Defaults to 0.
        """
        self.user_label = ttk.Label(self, text='User UUID: ').grid(row=row, column=0, padx=15, pady=0)
        self.user_input = ttk.Entry(self, textvariable=self.user_uuid).grid(row=row, column=1, padx=10, pady=0)


class Content(ttk.Frame):
    def __init__(self, parent, doc_uuid, user_uuid, n):
        super().__init__(parent)
        self.parent = parent
        self.doc_uuid = doc_uuid
        self.user_uuid = user_uuid
        self.n = n


    def display_chart(self, fig) -> None:
        """Plot the given figure on the tab canvas

        Args:
            fig (matplotlib.figure.Figure): matplotlib figure instance
        """
        if fig is None:
            logger.warning('Invalid document UUID')
            return
        
        if  hasattr(self, 'plot_canvas'):
            self.remove_plot()

        self.plot_canvas = FigureCanvasTkAgg(fig, self)
        self.plot_canvas.draw()
        self.plot_canvas.get_tk_widget().grid(column=0, row=3, columnspan=4, rowspan=4, pady=0, sticky='NSEW')
        #.pack(side=tk.TOP, fill=tk.BOTH, expand=True)  #
        self.plot_canvas.get_tk_widget()


    def display_info_text(self, string_list: list, row: int = 1) -> None:
        """Display list of strings in gui

        Args:
            string_list (list): List of strings
        """
        self.info_label = ttk.Label(self, text='\n'.join(string_list)).grid(column=0, row=2, columnspan=4,pady=0, rowspan=4,  sticky='NSEW')
        #.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        #.grid(row=row, column=0, columnspan=6, rowspan=8, sticky=(tk.N, tk.S, tk.E, tk.W))


    def display_graph(self, path) -> None:
        """Open also likes graph in an imageviewer
        """
        if hasattr(self, 'image_label'):
            #self.image_label.destroy()
            logger.info('Pre-existing label')

        path = os.path.abspath(path)
        logger.info('Path to image: {}'.format(path))
        load = Image.open(path)
        self.im_render = ImageTk.PhotoImage(load)
        self.image_label = ttk.Label(self, image=self.im_render).grid(column=0, row=2, columnspan=4, pady=0, rowspan=4,  sticky='NSEW')
        #.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        #.grid(column=0, row=2, columnspan=6, rowspan=8,  sticky=(tk.N, tk.S, tk.E, tk.W))


    def remove_plot(self) -> None:
        """Remove the plot fromt the canvas
        """
        try:
            self.plot_canvas.get_tk_widget().destroy()
        except AttributeError as e:
            logger.warning(
                'Attempted to close non-existing or empty canvas. Error: {}'.format(e))


class Tab(ttk.Frame):
    """A tab class, handles the logic of constructing each tab and rendering content inside.

    Args:
        compute_data (ComputeData): An instance of the ComputeData class
        widget_fn (Tab -> None, optional): A function to determine the correct content to render inside the tab. Defaults to pass_fn.
        master (ttk.Notebook): Parent Notebook object to manage tabs. Defaults to None.
        doc (str, optional): Doc uuid initial value. Defaults to None.
        user (str, optional): user uid initial value. Defaults to None.
        n (int, optional): Number of display items initial value. Defaults to None.
    """
    def __init__(self, compute_data, widget_fn=pass_fn, master=None, doc: str=None, user: str=None, n: int=None):
        super().__init__(master)
        self.master = master

        self.doc_uuid = tk.StringVar(self.master, value=doc)
        self.user_uuid = tk.StringVar(self.master, value=user)
        self.n = tk.IntVar(self.master, value=n)

        self.controls = Controls(self, self.doc_uuid, self.user_uuid, self.n)
        self.controls.grid(row=0, rowspan=2, columnspan=10, padx=10, pady=5, sticky=(tk.N, tk.W))
        self.content = Content(self, self.doc_uuid, self.user_uuid, self.n)
        self.content.grid(row=1, rowspan=10, columnspan=10, pady=90, sticky=(tk.N, tk.E, tk.S, tk.W))

        self.compute_data = compute_data
        self.widget_fn = widget_fn

        self.on_open = None
        self.image_label = None
        widget_fn(self)


    def set_on_open(self, fn) -> None:
        """Define a function to call when the tab is opened

        Args:
            fn (Any -> None): Function to call on tab open
        """
        self.on_open = fn


    def get_n(self) -> int:
        """Get the value contained in the n IntVar inside the tab

        Returns:
            int|None: Either an int or None, depending on the value of n
        """
        n = self.n.get()
        if n == 0:
            n = None
        return n


    def check_doc_uuid(self) -> str:
        """Get the value contained in the doc_uuid StringVar inside the tab

        Returns:
            str|None: Either a valid string or None when its invalid
        """
        uuid = self.doc_uuid.get()
        if not check_doc_uuid(uuid):
            return None
        return uuid


    def check_user_uuid(self)-> str:
        """Get the value contained in the user_uuid StringVar inside the tab

        Returns:
            str|None: Either a valid string or None when its invalid
        """
        uuid = self.user_uuid.get()
        if not check_user_uuid(uuid):
            return None
        return uuid


    def display_also_likes_text(self) -> None:
        """Display also likes information
        """

        al_iter = enumerate(self.find_also_likes())
        also_likes_list = []
        for i, e in al_iter:
            display_string = '{:{width}} | {}'.format(i, e, width=4)
            also_likes_list.append(display_string)
        self.content.display_info_text(also_likes_list, row=2)


    def plot_doc_continents(self) -> matplotlib.figure.Figure:
        """Plot the continents for a specific doc uuid

        Returns:
            matplotlib.figure.Figure: matplotlib figure instance
        """
        n = self.get_n()

        uuid = self.check_doc_uuid()
        try:
            self.compute_data.construct_document_counts_figure(
                uuid, show_countries=False, n_continents=n)
            return self.compute_data.histogram()
        except:
            logger.exception(
                'Exception encountered trying to plot doc uuid continents')


    def plot_doc_countries(self) -> matplotlib.figure.Figure:
        """Plot the countries for a specific doc uuid

        Returns:
            matplotlib.figure.Figure: matplotlib figure instance
        """
        n = self.get_n()

        uuid = self.check_doc_uuid()
        try:
            self.compute_data.construct_document_counts_figure(
                uuid, show_continents=False, n_countries=n)
            return self.compute_data.histogram()
        except:
            logger.exception(
                'Exception encountered trying to plot doc uuid countries')


    def plot_browser_counts(self, clean_browser_names: bool = True) -> matplotlib.figure.Figure:
        """Plot the browser counts for an entire input file

        Args:
            clean_browser_names (bool, optional): Provide a plot with clean browser names. Defaults to True.

        Returns:
            matplotlib.figure.Figure: matplotlib figure instance
        """
        n = self.get_n()

        self.compute_data.construct_counts_figure(
            show_continents=False, show_countries=False, n_browsers=n, clean_browser_names=clean_browser_names)
        return self.compute_data.histogram()


    def display_reader_profiles(self) -> None:
        """Display reader profile information in the tab
        """
        n = self.get_n()
        self.compute_data.sort(sort_countries=False,
                                      sort_continents=False, sort_browsers=False)

        if n is None:
            n = 10

        profile_list = []
        profile_iter = iter(self.compute_data.reader_profiles.values())

        for i in range(0, n):
            profile = next(profile_iter)
            display_string = '{:{width}} | {}'.format(i, profile, width=4)
            print(display_string)
            profile_list.append(display_string)

        self.content.display_info_text(profile_list)


    def find_also_likes(self) -> list:
        """Pass gui parameters into also likes function

        Returns:
            list: list of also like documents
        """
        try:
            n = self.get_n()
            doc_uuid = self.check_doc_uuid()
            user_uuid = self.check_user_uuid()
            if n is None:
                n = 10
            return self.compute_data.also_likes(doc_uuid, user_uuid, sort_fn=top_n_sorted, n=n)
        except:
            logger.exception('Exception encountered acquiring also likes')


    def display_also_likes_graph(self):
        doc_uuid = self.check_doc_uuid()
        user_uuid = self.check_user_uuid()
        n = self.get_n()
        #directory =WORK_DIR +
        #logger.info(directory)
        graph = Graphs(self.compute_data, 'also_likes')
        self.digraph = graph.also_likes_graph(doc_uuid, user_uuid, n)
        path = graph.save_view_graph(self.digraph)
        self.content.display_graph(path)
