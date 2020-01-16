'''
Created on Dec 16, 2019

@author: corymilsap
'''

import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askdirectory
#from GUI.Login import LoginFrame
from GUI.SearchFrame import SearchPage
import DataIO.SECDataMiner as dm
import subprocess
import os
import CIMGColors as color


"""
***     Use this code as a framework for restructuring    ***

import tkinter as tk

class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        <create the rest of your GUI here>

if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
"""


class MainView(tk.Frame):
    def __init__(self, *args, **kwargs):
        def selectFolder(event):
            global downloadPath
            downloadPath = askdirectory(title = 'Please Select a Download Location', initialdir = downloadPath)
            
        def companySearch(event):

            s = ttk.Style()
            s.theme_use("alt")
            s.configure("red.Horizontal.TProgressbar", foreground = color.red, background = color.red)
            ticker = searchP.searchFrame.searchEntry.get()
            
            errorLabel = tk.Label(searchP.searchFrame, text = "Ticker not found!", font = "Arial 24 bold", fg = "white")
            errorLabel.configure(fg = "white")
            errorLabel.grid(row = 3, column = 1)
            
            progress = ttk.Progressbar(searchP.searchFrame, style = "red.Horizontal.TProgressbar", length = 292)
            progress.grid(row = 3, column = 1)
            
            filingDocs = list()
            print(downloadPath)
            
            # We will raise an exception if the company is unable to be found
            try:
                filingDocs = dm.getDocumentsPage(ticker, "10-K")
                length = len(filingDocs)
                if length == 0: raise IndexError
                path = ""
                for i, doc in enumerate(filingDocs):
                    try:
                        statementsData = dm.pullFinancialStatements(doc)
                        path = dm.writeToExcel(ticker, statementsData, doc, "10-K", downloadPath)
                        progress["value"] = (i + 1) / length * 100
                        self.update()
                    except AttributeError:
                        break
                
                progress["value"] = 100
                progress.grid_remove()
                subprocess.call(["open", "-R", path])
                
            except IndexError:
                progress.grid_remove()
                errorLabel.configure(fg = color.red)
           
                    
        tk.Frame.__init__(self, *args, **kwargs)
        searchP = SearchPage(self)
        
        searchP.pack(fill = "both", expand = True)
        searchP.searchFrame.searchEntry.bind("<Return>", companySearch)
        searchP.searchFrame.goLabel.bind("<ButtonPress>", companySearch)
        searchP.searchFrame.folderIcon.label.bind("<ButtonPress>", selectFolder)

def start():
    
    global downloadPath
    downloadPath = os.getcwd()
    
    window = tk.Tk()
    window.title("CIMG Search Page")
    main = MainView(window)
    main.pack(side = "top", fill = "both", expand = True)
    window.minsize(700, 450)
    window.mainloop()
    
    