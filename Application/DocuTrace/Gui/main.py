import tkinter as tk
from tkinter import ttk

from DocuTrace.Gui.Tab import Tab, tab_dict
from DocuTrace.Utils.Logging import logger

class GuiRoot(tk.Tk):

    def __init__(self, compute_data, doc_uuid=None, user_uuid=None, n=None):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.geometry('850x750')
        #self.resizable(False, False)
        self.title('DocuTrace')
        self.tabs = ttk.Notebook(self)
        self.tabs.bind('<<NotebookTabChanged>>', on_tab_change)
        self.tabs.pack(expand=1, fill='both')
        self.tab_ref = {}

        for i, (k, v) in enumerate(tab_dict.items()):
            self.tab_ref[i] = Tab(compute_data, v, master=self.tabs, doc=doc_uuid, user=user_uuid, n=n)
            self.tabs.add(self.tab_ref[i], text=k)


    def on_close(self):
        """Stops shell from hanging when closing tkinter with matplotlib on canvas
        """
        self.quit()
        self.destroy()


    def start(self):
        """Begin main event loop
        """
        self.mainloop()





def on_tab_change(event):
    tab = event.widget.tab('current')['text']
    logger.warning('tab: {}'.format(tab))


def open(compute_data, doc_uuid=None, user_uuid=None, n=None):

    gui = GuiRoot(compute_data, doc_uuid, user_uuid, n)
    gui.start()



    # task_2a = Tab(compute_data, task2a_widgets, master=tabs, doc=doc_uuid, n=n)
    # tabs.add(task_2a, text='Task 2a')

    # task_2b = Tab(compute_data, task2b_widgets, master=tabs, doc=doc_uuid, n=n)
    # tabs.add(task_2b, text='Task 2b')

    # task_3a = Tab(compute_data, master=tabs)
    # tabs.add(task_3a, text='Task 3a')

    # task_3b = Tab(compute_data, master=tabs)
    # tabs.add(task_3b, text='Task 3b')

    # task_4 = Tab(compute_data, master=tabs)
    # tabs.add(task_4, text='Task 4d')

    # task_5d = Tab(compute_data, master=tabs)
    # tabs.add(task_5d, text='Task 5')

    # task_6 = Tab(compute_data, master=tabs)
    # tabs.add(task_6, text='Task 6')


    


