import tkinter as tk
from tkinter import ttk

from DocuTrace.Gui.Tab import Tab, tab_dict
from DocuTrace.Utils.Logging import logger

class GuiRoot(tk.Tk):

    def __init__(self, compute_data, doc_uuid=None, user_uuid=None, n=None, start_tab: str=None):
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
        tab_name = event.widget.tab('current')['text']
        logger.debug('tab: {}'.format(tab_name))
        tab = self.tab_ref[tab_name]
        tab.on_open()


def open(*args, **kwargs):

    gui = GuiRoot(*args, **kwargs)
    gui.start()



    


