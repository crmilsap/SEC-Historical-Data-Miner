'''
Created on Jan 16, 2020

This file's purpose is to download stock chart data from Yahoo Finance and create an Excel chart of the data for a given amount of years
@author: corymilsap
'''

import yfinance as yf     # Module found online to simplify grabbing data from Yahoo Finance since they discontinued their historical API
from datetime import datetime
import pandas as pd
import CIMGColors
import os

def downloadData(url):
    pass

def subtractYears(date, years):
    try:
        date = date.replace(year = date.year - years)
    except ValueError:
        date = date.replace(year = date.year - years, day = date.day - 1)
    return date

# Helper function to create a string for the range of excel cells that are needed 
def getExcelRange(col, colLength):
    cells = '=Chart!$' + col + '$2:$' + col + '$' + str(colLength + 1)
    return cells 

def writeChartToFile(dataframe, numYears, ticker, downloadPath):
    
    path = downloadPath + '/CIMG Downloads/' + ticker + '/'
    
    if not os.path.exists(path):
        os.makedirs(path)
        
    path += str(numYears) + ' Year Stock Chart.xlsx'
    writer = pd.ExcelWriter(path, engine = 'xlsxwriter')
    dataframe.to_excel(writer, sheet_name = 'Chart')
    workbook = writer.book
    worksheet = writer.sheets['Chart']
    worksheet.set_column('A:A', 20)
    
    colLength = len(dataframe.index)
    
    lineChart = workbook.add_chart({'type': 'line'})
    lineChart.add_series({
        'categories':   getExcelRange('A', colLength),
        'values':       getExcelRange('B', colLength),
        'line':         {'color': CIMGColors.darkBlue},

    })
    
    columnChart = workbook.add_chart({'type': 'column'})
    columnChart.add_series({
        'categories':   getExcelRange('A', colLength),
        'values':       getExcelRange('C', colLength),
        'y2_axis':      True,
        'fill':         {'color': CIMGColors.babyBlue},
    })
    columnChart.set_y2_axis({
        'label_position':   'none',
        'line':             {'none': True}
    })
    lineChart.combine(columnChart)
    
    lineChart.set_x_axis({
        'date_axis':        True,
        'num_format':       'mmm-yy',
        'num_font':         {'bold': True },
        'minor_unit':       3,
        'major_unit':       5,
        'minor_unit_type':  'months',
        'major_unit_type':  'months', 
        'line':         {'color': 'black'},
    })
    
    lineChart.set_y_axis({
        'major_gridlines':  {'visible': False,},
        'num_font':         {'bold': True},
        'num_format':       '$#,##0',
        'line':         {'color': 'black'},
    })
    lineChart.set_legend({'none': True})
    lineChart.set_chartarea({
        'border': {'none': True}
    })
    worksheet.insert_chart('E2', lineChart)

    writer.save()
    return path

def createChartFromYahoo(ticker, numYears, downloadPath):
        
        currentDate = datetime.now()
        endDate = datetime.now().strftime('%Y-%m-%d')
        startDate = subtractYears(currentDate, numYears).strftime('%Y-%m-%d')
        
        stock = yf.Ticker(ticker)
        history = stock.history(start = startDate, end = endDate, actoins = False)
        
        # Clean up the data frame to only store the information we want
        del history["Open"]
        del history["High"]
        del history["Low"]
        del history["Dividends"]
        del history["Stock Splits"]
        
        path = writeChartToFile(history, numYears, ticker, downloadPath)
        return path
        
