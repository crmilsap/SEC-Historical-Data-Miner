'''
Created on Dec 17, 2019

@author: corymilsap
'''
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup
import pandas as pd
import xlsxwriter
import os
import re
import CIMGColors
from math import isnan
# Gets historical 10-K's


"""
123.4

2.97
297
(2.97)
[2.97]
[1]
"""
def getDateOfFiling(dateString):
    yearStr = dateString[0:4]
    return int(yearStr)
 
def getDocumentsPage(ticker, filing):
    url = 'https://www.sec.gov/cgi-bin/browse-edgar?CIK=' + ticker + '&type=' + filing + '&dateb=&owner=exclude&start=0&count=40'
    sourceCode = requests.get(url)
    plainText = sourceCode.text
    soup = BeautifulSoup(plainText, features = "html.parser")
    
    table = soup.findAll("table")
    tableRows = table[2].findAll("tr")
    del tableRows[0] #This row is for the heading on the table. Not useful for our purposes.
    
    hrefs = list()
    #Gets all data from the rows of the table
    for tr in tableRows: #For single row in table
        td = tr.find_all("td")
        row = [i.text for i in td] #Gets info from row
        #year = getDateOfFiling(row[3]) This code works. May be useful if need to use the year later on.
        
        if row[0] == filing and "Interactive Data" in row[1]: # We only want the Forms that have the Interactive Data tab because this makes it easier to find the statements.
            # It is possible we want to add functionality to deal with the older data in the future. I.D. only goes to ~2010.
            link = tr.findAll("a", {"id": "documentsbutton"})
            hrefs.append("https://www.sec.gov" + link[0].get("href"))
    return hrefs
    
def getHTMLFiling(url): #Use this on the filingDocs list to get the filing in HTML format (if it is uploaded after 2006)
    sourceCode = requests.get(url)
    plainText = sourceCode.text
    soup = BeautifulSoup(plainText, features = "html.parser")
    
    table = soup.findAll("table", {"summary": "Document Format Files"})
    tableRows = table[0].findAll("tr")
    td = tableRows[1].find_all("td") #Take first row of table. This is where the filing (10-K or 10-Q) is stored.
    row = [i.text for i in td]
    
    if not (row[3] == '10-K' or row[3] == "10-Q"): # Acts as a checkpoint to make sure we are grabbing the correct file.
        raise Exception("Having trouble accessing the correct file.")
    
    href = td[2].findAll("a")
    docLink = "https://www.sec.gov" + href[0].get("href")
    
    return docLink
    
def formatDataFrame(df, title, headers):
    #Reformatting Data Frame to make it nicer.
    df.index = df[0]
    df.index.name = title
    df = df.drop(0, axis = 1)
    df.columns = headers
    
    # Get rid of extraneous characters so we can do math.
    df = df.replace("[\$,)]", "", regex = True)
    df = df.replace("[(]", "-", regex = True)
    df = df.replace("", "NaN", regex = True)
    
    #Convert Data to float
    df = df.astype(float)
    
    return df

def getNotableIndices(row, num):
    indices = []
    for index, entry in reversed(list(enumerate(row))):
        if "" != entry and "[" not in entry:
            indices.append(index)
            if len(indices) == num:
                break
    return indices

def DFForIncome10K(statementData): # This function will create a Data Frame for the Income Statement
    title = statementData["headers"][0][0]
    headers = statementData["headers"][1][-3:]

    data = []
    indices = []
    i = 0
    
    #We only want the first (it's the category) and last three data columns because these display the info about the whole year.
    while len(indices) != 3:
        indices = getNotableIndices(statementData["data"][i], 3)
        i += 1
      
    for row in statementData["data"]:
        newRow = []
        try:
            if "[" in row[0][0]:
                break 
            newRow.append(row[0])
            newRow.append(row[indices[2]])
            newRow.append(row[indices[1]])
            newRow.append(row[indices[0]])
        except IndexError:
            continue
        data.append(newRow)
    
    
    df = pd.DataFrame(data)
    df = formatDataFrame(df, title, headers)
    
    
    return df
  
def DFForBalanceSheet10K(statementData): 
    title = statementData["headers"][0][0]
    headers = statementData["headers"][0][-2:]

    data = []
    #There are three columns we want. The first which is the category and the two with numbers in the first row.
    #In order to get the correct row we must get the index of the columns.
    indices = []
    i = 0
    while len(indices) != 2:
        indices = getNotableIndices(statementData["data"][i], 2)
        i += 1
      
    for row in statementData["data"]:
        if (len(row) >= 3):
            newRow = []
            # If the row does not have the correct number of indices we will pass over it and continue the loop.
            try:
                if "[" in row[0][0]:
                    break 
                newRow.append(row[0])
                newRow.append(row[indices[1]])
                newRow.append(row[indices[0]])
            except IndexError:
                continue
            data.append(newRow)
    
    
    df = pd.DataFrame(data)
    df = formatDataFrame(df, title, headers)
    
    return df
      
def DFForCashFlows10K(statementData):
    title = statementData["headers"][0][0]
    headers = statementData["headers"][1][-3:]
    for i, s in enumerate(headers):
        s = s.replace("\n", "")
        s = s.replace("USD ($)", "")
        headers[i] = s
        
    data = []
    indices = []
    i = 0
    while len(indices) != 3:
        indices = getNotableIndices(statementData["data"][i], 3)
        i += 1
      
    for row in statementData["data"]:
        if (len(row) >= 3):
            newRow = []
            try:
                if "[" in row[0][0]:
                    break 
                newRow.append(row[0])
                newRow.append(row[indices[2]])
                newRow.append(row[indices[1]])
                newRow.append(row[indices[0]])
            except IndexError:
                continue
            data.append(newRow)
    
    df = pd.DataFrame(data)
    
    df = formatDataFrame(df, title, headers)
    
    return df
    
def pullFinancialStatements(link):
    
    link = link[:-30]
    baseLink = link
    link += "FilingSummary.xml" #This will take us to the page with a summary of the Filing that we are looking at in XML format.
    print(link)
    content = requests.get(link).content
    soup = BeautifulSoup(content, features = "lxml")
    reports = soup.find("myreports")
    statementsList = []
    
    for report in reports.find_all("report")[:-1]: #Last report isn't a regular report so we will omit it.
        reportDictionary = {}
        reportDictionary["shortName"] = report.shortname.text
        reportDictionary["longName"] = report.longname.text
        reportDictionary["url"] = baseLink + report.htmlfilename.text
    
        #These are the reports we want to pull
        incomeStatementNames = ["consolidated statements of operations", "consolidated income statement", "income statements", "consolidated statements of income", "consolidated statements of earnings", "consolidated and sector income statement", "consolidated and sector statement of operations", "statements of operations"]
        balanceSheetNames = ["consolidated statements of financial position", "consolidated balance sheet", "consolidated balance sheets", "balance sheets", "consolidated and sector balance sheet", "consolidated statements of financial condition" ]
        cashFlowStatementNames = ["consolidated statements of cash flows", "consolidated statement of cash flows", "cash flows statements", "consolidated statements of cash flows", "consolidated and sector statement of cash flows", "consolidated statements of cash flows statement"]
        desiredList = []
        desiredList.extend(incomeStatementNames)
        desiredList.extend(balanceSheetNames)
        desiredList.extend(cashFlowStatementNames)
        
      
        if reportDictionary["shortName"].lower() in desiredList:
                statementsList.append(reportDictionary)
                if len(statementsList) == 3: break
       
    statementsData = {}

    
    # Now we will loop through all the data we determined is relevant and store that.
    for statement in statementsList:
        
        # Define a dictionary that will store the different parts of the statement.
        statementData = {}
        statementData["headers"] = []
        statementData["sections"] = []
        statementData["data"] = []
        
        
        content = requests.get(statement["url"]).content
        soup = BeautifulSoup(content, "html.parser")
        for row in soup.findAll('tr'):
           
            cols = row.find_all('td') 
            
            # A regular row has no th tags
            if (len(row.find_all("th")) == 0):
                if len(row) > 1 and row.td.text != "X": # Lots of hidden rows will mess up data frame
                    regRow = []
                    regRow.append(cols[0].text.strip())
                    
                    for e in cols[1:]:
                        e = e.text.strip()
                        re.sub(r"[^0-9\.\(\[]", "", e) # Replaces all characters that are not digits, [ or ( 
                        e = "".join(filter(lambda x: x.isdigit() or x == "(" or x == "[" or x == ".", e))
                        regRow.append(e)
                        
                                
                    statementData["data"].append(regRow)
                
            # A header has th tags
            elif (len(row.find_all("th")) != 0):
                headerRow = [e.text.strip() for e in row.find_all("th")]
                statementData["headers"].append(headerRow)
            else:
                print("We encountered an error")
        
        if statement["shortName"].lower() in incomeStatementNames:
            incomeDF = DFForIncome10K(statementData)
            statementsData["incomeStatement"] = incomeDF

        elif statement["shortName"].lower() in balanceSheetNames:
            balanceDF = DFForBalanceSheet10K(statementData)    
            statementsData["balanceSheet"] = balanceDF
            
        elif statement["shortName"].lower() in cashFlowStatementNames:
            cashFlowsDF = DFForCashFlows10K(statementData)
            statementsData["cashFlow"] = cashFlowsDF
    
    return statementsData   

def formatTitleCells(formatTitle): # Basic title format for each sheet
    formatTitle.set_bold()
    formatTitle.set_font_color("white")
    formatTitle.set_center_across()
    formatTitle.set_align("vcenter")
    formatTitle.set_bg_color(CIMGColors.darkBlue)
    
    return formatTitle

def formatHeaderCells(formatHeader):
    formatHeader.set_bold()
    formatHeader.set_font_color("white")
    formatHeader.set_bg_color(CIMGColors.darkBlue)
    formatHeader.set_align("center")
    formatHeader.set_align("bottom")
    
    return formatHeader

def formatIndexCells(formatIndex, bold):
    
    formatIndex.set_align("right")
    formatIndex.set_right(1)
    
    if bold is True:
        formatIndex.set_bold()
        
    return formatIndex

def formatDataCells(formatData):
    formatData.set_align("center")
    formatData.set_bottom(1)
    formatData.set_num_format("#,###")
    
    return formatData

def formatExcel(workbook, statementName, statementData):
    sheet = workbook.add_worksheet(statementName)

    # Basic sheet formatting
    sheet.hide_gridlines(2)
    sheet.set_column(2, 2, 40)
    sheet.set_column(3, 5, 12)
    sheet.set_default_row(20)
    
    title = statementData.index.name
    dates = statementData.columns
    
    # Gets all formatting we need
    formatTitle = workbook.add_format()
    formatTitle = formatTitleCells(formatTitle)
    formatHeader = workbook.add_format()
    formatHeader = formatHeaderCells(formatHeader)
    formatIndex = workbook.add_format()
    formatIndex = formatIndexCells(formatIndex, False)
    formatBoldIndex = workbook.add_format()
    formatBoldIndex = formatIndexCells(formatBoldIndex, True)
    formatData = workbook.add_format()
    formatData = formatDataCells(formatData)
    
    # Writes title
    sheet.write("C4", title, formatTitle)
    sheet.write("D4", "", formatTitle)
    sheet.write("E4", "", formatTitle)
    if statementName != "Balance Sheet":
        sheet.write("F4", "", formatTitle)
    
    # Writes date headers
    sheet.write(4, 2, "", formatHeader) 
    for i, d in enumerate(dates):
        sheet.write(4, i+3, d, formatHeader)
    
    # Add data
    for i, row in enumerate(statementData.iterrows()):
        name, data = row
        rowIsHeaderFlag = True
        if "- Definition" in name: #Removes a bunch of junk at the end of older files
            break
        
        for d in data:
            
            if not isnan(d):
                rowIsHeaderFlag = False
            
        if rowIsHeaderFlag == True:
            sheet.write(i + 5, 2, name, formatBoldIndex)
        else:
            sheet.write(i + 5, 2, name, formatIndex)
        
    
        for j, r in enumerate(data):
            try:
                sheet.write(i + 5, j + 3, r, formatData)
            except TypeError:
                sheet.write(i + 5, j + 3, "", formatData)
                
    return sheet
   
def writeToExcel(ticker, statementsData, urlToDoc, filingType, downloadPath):
    year = statementsData["incomeStatement"].columns[0][-4:]
    path = downloadPath + "/Reports/" + ticker + "/" + year + "/"
    if filingType == "10-K":
        filename = path + ticker + "FY" + str(year)[-2:] + ".xlsx"
    else:
        filename = path + ticker + filingType + ".xlsx"
        
    filingURL = getHTMLFiling(urlToDoc)
    filingURL = filingURL.replace("ix?doc=", "")
    if not os.path.exists(path):
        os.makedirs(path)
        
    html = urlopen(filingURL)
    page_content = html.read()
    with open(path + filingType + ".html", "wb") as f:
        f.write(page_content)
    
    with pd.ExcelWriter(filename) as writer:
        workbook = writer.book
        incomeSheet = formatExcel(workbook, "Income Statement", statementsData["incomeStatement"])
        balanceSheet = formatExcel(workbook, "Balance Sheet", statementsData["balanceSheet"])
        cashFlows = formatExcel(workbook, "Cash Flows", statementsData["cashFlow"])
        
        workbook.close()
    
    return path # Returns the directory path so we can open it in the OS

def companySearch(ticker, documentType = "10-K"):
    
    filingDocs = list()
    filingDocs = getDocumentsPage(ticker, documentType)[0]
    length = len(filingDocs)
    for i, doc in enumerate(filingDocs):
        try:
            statementsData = pullFinancialStatements(doc)
            writeToExcel(ticker, statementsData, doc, documentType, downloadPath)
            print("Progress: {}%".format( (i + 1) / length * 100))
        except AttributeError:
            break
    
    print("Complete")

# This code can get us the direct links to filings. Useful
# getHTMLFiling(filingDocs[0])
# for i in filingDocs:
#     temp = getHTMLFiling(i)
#     goalDocuments.append(temp)
#     print(temp)

#Consolidated Statements Of Operations - Income Statement
#Consolidated Statements Of Financial Position - Balance Sheet
#Consolidated Statements of Cash Flows - Cash Flow Statement
