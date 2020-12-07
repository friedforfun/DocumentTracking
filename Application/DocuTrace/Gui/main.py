import tkinter as tk
from tkinter import ttk

from DocuTrace.Gui.Tab import Tab, tab_dict
from DocuTrace.Utils.Logging import logger

class GuiRoot(tk.Tk):
    """Root GUI element, this class handles window size, instantiates the actual gui content and binds events to functions.

    Args:
        compute_data (ComputeData): An instance of the ComputeData class
        doc_uuid (str, optional): A document uuid. Defaults to None.
        user_uuid (str, optional): A user uuid. Defaults to None.
        n (int, optional): A number indicating how many elements to display in the content frame. Defaults to None.
        start_tab (str, optional): The identifier of the tab to open first. Defaults to None.
    """
    def __init__(self, compute_data, doc_uuid: str=None, user_uuid: str=None, n: int=None, start_tab: str=None):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.geometry('850x750')
        #self.resizable(False, False)
        self.title('DocuTrace')
        self.tabs = ttk.Notebook(self)
        self.tabs.bind('<<NotebookTabChanged>>', self.on_tab_change)
        self.tabs.pack(expand=1, fill='both')
        self.tab_ref = {}

        for k, v in tab_dict.items():
            self.tab_ref[k] = Tab(compute_data, v, master=self.tabs, doc=doc_uuid, user=user_uuid, n=n)
            self.tabs.add(self.tab_ref[k], text=k)

        if start_tab:
            self.tabs.select(self.tab_ref[start_tab])


    def on_close(self):
        """Stops shell from hanging when closing tkinter with matplotlib on canvas
        """
        self.quit()
        self.destroy()


    def start(self):
        """Begin main event loop
        """
        self.mainloop()


    def on_tab_change(self, event):
        """This method is called when a tab is changed, the event is passed as a parameter

        Args:
            event (tkinter.Event): This is the event object, holds details of the object that triggered this event.
        """
        tab_name = event.widget.tab('current')['text']
        logger.debug('tab: {}'.format(tab_name))
        tab = self.tab_ref[tab_name]
        tab.on_open()


def open(*args, **kwargs):
    """Function to start gui
    """
    gui = GuiRoot(*args, **kwargs)
    gui.start()



    


