
from DocuTrace.Utils.Logging import logger
import matplotlib
import random
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #NavigationToolbar2TkAgg
import tkinter as tk
from tkinter import ttk

# from matplotlib import style

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
        widget_fn(self)
        self.btn_close_plot = ttk.Button(self.master, text='Close plot', command=self.remove_plot).grid(row=0, column=10, pady=30)



    def plot_doc_countries(self):
        self.compute_data.construct_document_counts_figure(
            self.doc_uuid.get(), show_continents=False, n_countries=self.n.get())
        return self.compute_data.histogram()


    def display_chart(self, fig):
        self.plot_canvas = FigureCanvasTkAgg(fig, self)
        self.plot_canvas.draw()
        self.plot_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        

    def remove_plot(self):
        try:
            self.plot_canvas.get_tk_widget().destroy()
        except AttributeError as e:
            logger.warning('Attempted to close non-existing or empty canvas. Error: {}'.format(e))



def on_close(root):
    """Stops shell from hanging when closing tkinter with matplotlib on canvas

    Args:
        root (tkinter.Tk): Tikinter root component
    """
    root.quit()
    root.destroy()


def doc_input(master, doc_stringvar, btn_fn):
    label = ttk.Label(master, text='Document UUID: ').grid(row=0, column=0, padx=30, pady=30)

    input = ttk.Entry(master, textvariable=doc_stringvar)
    input.grid(row=0, column=1, padx=5, pady=30)

    button = ttk.Button(master, text='Go', command=btn_fn)
    button.grid(row=0, column=2, padx=5, pady=30)

    return label, input, button


def task2a_widgets(tab):
    tab.label_doc_uuid, tab.input_doc_uuid, tab.btn_doc_uuid = doc_input(tab.master, tab.doc_uuid, lambda: tab.display_chart(tab.plot_doc_countries()))
    tab.label_n = ttk.Label(tab.master, text='Number to display: ').grid(row=1, column=0, padx=10, pady=0)
    tab.input_n = ttk.Entry(tab.master, textvariable=tab.n).grid(row=1, column=1, padx=5, pady=0)
    

    # tab.lbl_doc_uuid = ttk.Label(tab.master, text='Document UUID: ')
    # tab.lbl_doc_uuid.grid(row=0, column=0, padx=30, pady=30)
    # if tab.doc_uuid is None:
    #     tab.input_doc_uuid = ttk.Entry(tab.master)
    # else:
    #     tab.input_doc_uuid = ttk.Entry(tab.master, textvariable=tab.doc_uuid)
    # tab.input_doc_uuid.grid(row=0, column=1, padx=5, pady=30)

    # tab.btn_doc_uuid = ttk.Button(tab.master, text='Go', command=None)
    # tab.btn_doc_uuid.grid(row=0, column=2, padx=5, pady=30)


def open(compute_data, doc_uuid=None, user_uuid=None, n=None):

    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", lambda: on_close(root))
    root.geometry('700x700')
    #root.resizable(False, False)
    root.title('DocuTrace')

    tabs = ttk.Notebook(root)
    task_2a = Tab(compute_data, task2a_widgets, master=tabs, doc=doc_uuid, n=n)
    tabs.add(task_2a, text='Task 2a')

    task_2b = Tab(compute_data, master=tabs)
    tabs.add(task_2b, text='Task 2b')

    task_3a = Tab(compute_data, master=tabs)
    tabs.add(task_3a, text='Task 3a')

    task_3b = Tab(compute_data, master=tabs)
    tabs.add(task_3b, text='Task 3b')

    task_4 = Tab(compute_data, master=tabs)
    tabs.add(task_4, text='Task 4d')

    task_5d = Tab(compute_data, master=tabs)
    tabs.add(task_5d, text='Task 5')

    task_6 = Tab(compute_data, master=tabs)
    tabs.add(task_6, text='Task 6')


    tabs.pack(expand=1, fill='both')

    root.mainloop()
