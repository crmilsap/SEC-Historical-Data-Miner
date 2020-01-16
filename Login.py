'''
Created on Dec 15, 2019

@author: corymilsap
'''
import tkinter as tk
from PIL import Image, ImageTk
import CIMGColors

class HeaderFrame():
    def __init__(self, parent):
        # This code has to deal with the header at the top of the Login Page.
        topFrame = tk.Frame(parent, bg = CIMGColors.red)
        topFrame.pack(side = "top", fill = "x")
        
        titleIMG = ImageTk.PhotoImage(Image.open("../images/HeaderText.png"))
        titleLabel = tk.Label(topFrame, image = titleIMG, bg = CIMGColors.red)
        titleLabel.image = titleIMG
        titleLabel.pack()
        

class FooterFrame():
    def __init__(self, parent):
        #This creates the footer at the bottom of the page that holds the CIMG Logo.
        #Not currently used
        bottomFrame = tk.Frame(parent, bg = "white")
        bottomFrame.pack(side = "bottom", fill = "x")
        
        rightFrame = tk.Frame(bottomFrame, bg = CIMGColors.red)
        rightFrame.pack(side = "right")
        
        CIMGLogoIMG = ImageTk.PhotoImage(Image.open("../images/CIMGLogo3.jpg"))
        CIMGLogoLabel = tk.Label(rightFrame, image = CIMGLogoIMG)  
        CIMGLogoLabel.image = CIMGLogoIMG 
        CIMGLogoLabel.pack()
             
class LoginFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        username = password = "" # initializes the two variables for the frame
        
       
        header = HeaderFrame(self)
        
        # This is the code for the footer of the page. This consists of the login and register buttons.
        bottomFrame = tk.Frame(self, bg = "white", bd = 10)
        bottomFrame.pack(side = "bottom", fill = "x")
        
        # I use labels as buttons so that the platform appears the same on OSX and Windows
        registerLabel = tk.Label(bottomFrame, text = "Register", font = "Arial 24 bold", bg = CIMGColors.red, 
                              fg = "white", bd = 10, cursor = 'pointinghand')
        registerLabel.pack(side = "top", fill = "x", pady = (0, 5))
        self.loginLabel = tk.Label(bottomFrame, text = "Login", font = "Arial 24 bold", bg = CIMGColors.red, 
                           fg = "white", bd = 10, cursor = 'pointinghand')
        self.loginLabel.pack(side = "bottom", fill = "x")
        
        # The header and bottom buttons are now completed. Moving on to the Login portion.
        middleFrame = tk.Frame(self)
        middleFrame.pack(side = "left", fill = "x")
        usernameLabel = tk.Label(middleFrame, text = "Username:", font = "Arial 24 bold")
        usernameText = tk.Entry(middleFrame, textvariable = username)
        passwordLabel = tk.Label(middleFrame, text = "Password:", font = "Arial 24 bold")
        passwordText = tk.Entry(middleFrame, textvariable = password, show = "\u2022") #shows the bullet symbol
        remember = tk.Checkbutton(middleFrame, text = "Remember Me", font = "Arial 18", takefocus = 0)
        
        usernameLabel.grid(row = 0, padx = (50, 10))
        usernameText.grid(row = 0, column = 1, ipady = 5)
        passwordLabel.grid(row = 1, padx = (50, 10))
        passwordText.grid(row = 1, column = 1, ipady = 5, pady = 3)
        remember.grid(row = 2, column = 1, sticky = "w")
        
# root = tk.Tk()
# root.title("CIMG Login")
# main = LoginFrame(root)
# main.pack(side = "top", fill = "both", expand = True)
# root.minsize(700, 750)
# root.mainloop()
