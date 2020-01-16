# SEC-Historical-Data-Miner

This project began development in December 2019.

The purpose of this project is to streamline the process of gathering historical data on companies registered with the SEC.
The backend is contained within the SECDataMiner.py class and utilizes BeautifulSoup and Pandas dataframes to compile the information. It then uses XlsxWriter to write and format Excel documents for the user.

The front end of the project utilizes Tkinter in order to create a clean, easy-to-use GUI. The user simply enters the ticker of the company they wish to search and then and progress bar appears and the OS opens the directory where they selected to download their files (using the Windows File Explorer icon). 

In the directory the program also downloads and stores the filed document that it is reading from. This is to simplify the process of looking up the filing for the user in the event that they want to read more information or check to make sure the figures are correct. 

In the future, I plan to expand this project to create company tearsheets and historical files that show years of data in one file rather than a file for every year. I believe the biggest obstacle to this will be in the form of identifying the multitude of various line items as the same value from filing to filing. i.e. a company can call their revenue a variety of different names. 

Being busy with school and interested in starting other projects, I am uncertain how long this process will take.
