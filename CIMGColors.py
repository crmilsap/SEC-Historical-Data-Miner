'''
Created on Dec 15, 2019

@author: corymilsap
'''
from _curses import COLOR_YELLOW

#Takes an RGB value and converts to Hexadecimal
def RGBtoHex(r, g, b):
    return '#%02x%02x%02x' % (r, g, b)

darkBlue = '#012069'
babyBlue = '#6487be'
yellow = '#ffcc00'
orange = '#e47200'
maroon = '#6b2146'
veryLightBlue = '#ccd7ea'
green = '#00703c'
gray = '#afafaf'
turqoise = '#008987'
lightGreen = '#78b257'
red = '#831d1b'
magenta = '#ca8cb8'
violet = '#666699'
black = '#231f20'