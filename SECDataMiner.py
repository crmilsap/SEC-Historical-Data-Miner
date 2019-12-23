'''
Created on Dec 17, 2019

@author: corymilsap
'''
import requests
from bs4 import BeautifulSoup
import pandas as pd
import xlsxwriter
import os
import re

# Gets historical 10-K's

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
#     df = df.replace("[(]", "-", regex = True)
#     df = df.replace("", "NaN", regex = True)
    #Convert Data to float
    try:
        df = df.astype(float)
    except ValueError:
        print("VALUE ERROR@!!!!")
    
    return df
def DFForIncome10K(statementData): # This function will create a Data Frame for the Income Statement
    title = statementData["headers"][0][0]
    headers = statementData["headers"][1][-3:]
    
    data = []
    #We only want the first (it's the category) and last three data columns because these display the info about the whole year.
    for row in statementData["data"]:
        newRow = []
        newRow.append(row[0])
        lastThree = row[-3:]
        newRow.extend(lastThree)
        data.append(newRow)
    
    
    df = pd.DataFrame(data)
    df = formatDataFrame(df, title, headers)
    
    
    return df
  
def DFForBalanceSheet10K(statementData):
    title = statementData["headers"][0][0]
    headers = statementData["headers"][0][-2:]
    data = []
    #Sometimes there will be an additional column. We do not want this so I will exclude it.
    for row in statementData["data"]:
        if (len(row) >= 3):
            newRow = []
            newRow.append(row[0])
            lastTwo = row[-2:]
            newRow.extend(lastTwo)
            data.append(newRow)
    
    
    df = pd.DataFrame(data)
    df = formatDataFrame(df, title, headers)
    
    return df
      
def DFForCashFlows10K(statementData):
    title = statementData["headers"][0][0]
    headers = statementData["headers"][1][-3:]
    for s in headers:
        s.replace("\n", "")
        s.replace("USD ($)", "")
        
    data = statementData["data"]
    
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
        incomeStatementNames = ["consolidated statements of operations", "consolidated income statement", "income statements"]
        balanceSheetNames = ["consolidated statements of financial position", "consolidated balance sheet", "consolidated balance sheets", "balance sheets"]
        cashFlowStatementNames = ["consolidated statements of cash flows", "consolidated statement of cash flows", "cash flows statements"]
        desiredList = []
        desiredList.extend(incomeStatementNames)
        desiredList.extend(balanceSheetNames)
        desiredList.extend(cashFlowStatementNames)
        
        if reportDictionary["shortName"].lower() in desiredList:
                statementsList.append(reportDictionary)
       
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
            
            # A regular row has no th tags and no strong tags
            if (len(row.find_all("th")) == 0 and len (row.find_all("strong")) == 0):
                if len(row) > 1 and row.td.text != "X": # Lots of hidden rows will mess up data frame
                    regRow = []
                    regRow.append(cols[0].text.strip())
                    for e in cols[1:]:
                        
                        if e.has_attr("class"):
                            print(e.get("class"))
                            if (e.get("class")[-1:] in "nump"):
                                e = e.text.strip()
                                e = re.sub("[^0-9()]", "", e)
                                regRow.append(e)
                                
                    statementData["data"].append(regRow)
                
            # A section head has no th but has strong properties
            elif (len(row.find_all("th")) == 0 and len (row.find_all("strong")) != 0):
                sectionRow = cols[0].text.strip()
                statementData["sections"].append(sectionRow)
                
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
        
def writeToExcel(ticker, statementsData):
    year = statementsData["incomeStatement"].columns[0][-4:]
    path = "../../Reports/" + ticker + "/" + year + "/"
    filename = path + ticker + str(year) + ".xlsx"
    
    if not os.path.exists(path):
        os.makedirs(path)
    with pd.ExcelWriter(filename) as writer:
        statementsData["incomeStatement"].to_excel(writer, startrow = 4, startcol = 4, sheet_name = "Income Statement")
        statementsData["balanceSheet"].to_excel(writer, startrow = 4, startcol = 4, sheet_name = "Balance Sheet")
        statementsData["cashFlow"].to_excel(writer, startrow = 4, startcol = 4, sheet_name = "Cash Flows")
    


filingDocs = list()
goalDocuments = list() #This will store the links to the actual 10-K's or 10-Q's
ticker = "BA"
filingDocs = getDocumentsPage(ticker, "10-K")
for doc in filingDocs[0:1]:
    statementsData = pullFinancialStatements(doc)
    writeToExcel(ticker, statementsData)

# This code can get us the direct links to filings. Useful
# getHTMLFiling(filingDocs[0])
# for i in filingDocs:
#     temp = getHTMLFiling(i)
#     goalDocuments.append(temp)
#     print(temp)

#Consolidated Statements Of Operations - Income Statement
#Consolidated Statements Of Financial Position - Balance Sheet
#Consolidated Statements of Cash Flows - Cash Flow Statement
