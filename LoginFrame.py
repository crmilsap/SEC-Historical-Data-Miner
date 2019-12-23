'''
Created on Dec 15, 2019

@author: corymilsap
'''
from tkinter import *
from PIL import Image, ImageTk
import CIMGColors

root = Tk(className = "CIMG Login")
root.minsize(700, 750)

username = password = "" # initializes the two variables for the frame

# This code has to deal with the header at the top of the Login Page.
topFrame = Frame(root, bg = CIMGColors.darkBlue)
topFrame.pack(side = TOP, fill = X)

AImg = ImageTk.PhotoImage(Image.open("../../images/scriptA.png"))
scriptAFrame = Frame(topFrame, bg = CIMGColors.darkBlue)
scriptAFrame.pack(side = LEFT)
scriptALabel = Label(scriptAFrame, image = AImg, bg = CIMGColors.darkBlue)
scriptALabel.pack(padx = 20, pady = (20,10))

CIMGLogoIMG = ImageTk.PhotoImage(Image.open("../../images/CIMGLogo2.png"))
CIMGLogoFrame = Frame(topFrame, bg = CIMGColors.darkBlue)
CIMGLogoFrame.pack(side = RIGHT)
CIMGLogoLabel = Label(CIMGLogoFrame, image = CIMGLogoIMG, bg = CIMGColors.darkBlue)
CIMGLogoLabel.pack(padx = (10,20), pady = (20, 10), side = RIGHT)
CIMGWords = Label(CIMGLogoFrame, text = "Culverhouse Investment Management Group", fg = "white", 
                  bg = CIMGColors.darkBlue, justify = RIGHT, wraplength = 175, font = "Arial 24 bold")
CIMGWords.pack(side = LEFT)


# This is the code for the footer of the page. This consists of the login and register buttons.
bottomFrame = Frame(root, bg = "white", bd = 10)
bottomFrame.pack(side = BOTTOM, fill = X)

# I use labels as buttons so that the platform appears the same on OSX and Windows
registerLabel = Label(bottomFrame, text = "Register", font = "Arial 24 bold", bg = CIMGColors.darkBlue, 
                      fg = "white", bd = 10, cursor = 'hand')
registerLabel.pack(side = TOP, fill = X, pady = (0, 5))
loginLabel = Label(bottomFrame, text = "Login", font = "Arial 24 bold", bg = CIMGColors.darkBlue, 
                   fg = "white", bd = 10, cursor = 'hand')
loginLabel.pack(side = BOTTOM, fill = X)


# The header and bottom buttons are now completed. Moving on to the Login portion.
middleFrame = Frame(root)
middleFrame.pack(side = LEFT, fill = X)
usernameLabel = Label(middleFrame, text = "Username:", font = "Arial 24 bold")
usernameText = Entry(middleFrame, textvariable = username)
passwordLabel = Label(middleFrame, text = "Password:", font = "Arial 24 bold")
passwordText = Entry(middleFrame, textvariable = password, show = "\u2022") #shows the bullet symbol
remember = Checkbutton(middleFrame, text = "Remember Me", font = "Arial 18", takefocus = 0)

usernameLabel.grid(row = 0, padx = (50, 10))
usernameText.grid(row = 0, column = 1, ipady = 5)
passwordLabel.grid(row = 1, padx = (50, 10))
passwordText.grid(row = 1, column = 1, ipady = 5, pady = 3)
remember.grid(row = 2, column = 1, sticky = W)


root.mainloop()
