#!/usr/bin/python

import tkinter as tk
from tkinter.ttk import Notebook, Frame

class Tab(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Hello World\n(click me)"
        self.hi_there["command"] = lambda _: print('Hi')
        self.hi_there.pack(side="top", expand=True)

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")

def open():
    root = tk.Tk()
    root.geometry('500x500')
    root.title('DocuTrace')
    tabs = Notebook(root)
    task_2a = Tab(master=tabs)
    tabs.add(task_2a, text='Task 2a')

    task_2b = Tab(master=tabs)
    tabs.add(task_2b, text='Task 2b')

    task_3a = Tab(master=tabs)
    tabs.add(task_3a, text='Task 3a')

    task_3b = Tab(master=tabs)
    tabs.add(task_3b, text='Task 3b')

    task_4d = Tab(master=tabs)
    tabs.add(task_4d, text='Task 4d')

    task_5 = Tab(master=tabs)
    tabs.add(task_5, text='Task 5')

    task_6 = Tab(master=tabs)
    tabs.add(task_6, text='Task 6')


    tabs.pack(expand=1, fill='both')

    root.mainloop()
