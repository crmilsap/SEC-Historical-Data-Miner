'''
Created on Dec 29, 2019

@author: corymilsap

'''
import tkinter as tk
from GUI.Login import HeaderFrame, FooterFrame
import CIMGColors as colors
from GUI import WidgetLibrary

class searchBox(tk.Frame):   
    def __init__(self, *args, **kwargs):
        def capAndLimitSize(*args):
            ticker.set(ticker.get().upper())
            text = ticker.get()
            if len(text) > 5: ticker.set(text[:5])

        tk.Frame.__init__(self, *args, **kwargs)
        
        ticker = tk.StringVar()
        
        searchLabel = tk.Label(self, text = "Search", font = "Arial 24")
        searchLabel.grid(row = 0, column = 0)
        
        self.goLabel = tk.Label(self,text = "Go", font = "Arial 24", bg = colors.red, fg = "white", bd = 5, relief = "groove", cursor = "pointinghand")
        self.goLabel.grid(row = 2, column = 1, pady = 50, ipadx = 122)
        
        self.searchEntry = tk.Entry(self, textvariable = ticker, font = "Arial 24 bold", width = 20, justify = "left", highlightbackground = colors.red)
        self.searchEntry.grid(row = 0, column = 1)
        
        self.folderIcon = WidgetLibrary.BrowseFolderButton(self)
        self.folderIcon.grid(row = 0, column = 2, padx = 7)
        
        ticker.trace_add("write", capAndLimitSize)
        
     
class SearchPage(tk.Frame):

    
    
    def __init__(self, *args, **kwargs):

        tk.Frame.__init__(self, *args, **kwargs)
        
        ticker = tk.StringVar()
        
        header = HeaderFrame(self)
        
        
        
        blankBottom = tk.Frame(self, bg = "white")
        blankBottom.pack(side = "bottom")
        
        self.searchFrame = searchBox(self)
        self.searchFrame.pack(padx = (10, 40), pady = 100)
        

# root = tk.Tk()
# root.title("CIMG Company Search")
# main = SearchPage(root)
# main.pack(side = "top", fill = "both", expand = True)
# root.minsize(700, 450)
# root.mainloop()
