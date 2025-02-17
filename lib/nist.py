import requests, re
from time import sleep
from bs4 import BeautifulSoup
import lib.processVector as processVector
import lib.processCPE as processCPE 
import lib.setRandomUserAgent as getRandomUserAgent
def queryNist(cveNumber):
    """
    This function takes in the CVE numbers from the txt file given through another function called fileInput
    With each CVE number, it then attempts to concatenate 'site:https://nvd.nist.gov/vuln/detail/' to try to get more data through the nvd.nist.gov website.
    Information that this function retrieves:
    - CVSS Score 
    - Vector String (e.g. CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H), which then makes use of another function called decodeFunc to break up the string and extract usable data from it.
    - A list of CPE Strings (e.g. cpe:2.3:a:transmissionbt:transmission:*:*:*:*:*:*:*:*), which then makes use of another function called cpeExtractor to break up the strings and extract more usable data from them.
    """
    headers = getRandomUserAgent.random_userAgent()
    cveSearch = 'https://nvd.nist.gov/vuln/detail/' + cveNumber #Makes use of google dorking to search for results from nvd.nist.gov
    try:
        sleep(5)
        searchResults = requests.get(cveSearch, headers=headers)
        response = searchResults.content
        soup = BeautifulSoup(response,'lxml')
        #Get the CVSS Score
        getCVSS = soup.find_all("div",{"class":"col-lg-3 col-sm-6"})
        cvssScore = re.findall("(\d{1,2}\.\d\s)\w+",str(getCVSS))[0]
        #Get the Description
        getDescriptionClass = soup.find("div",{"class":"col-lg-9 col-md-7 col-sm-12"})
        getDescription = getDescriptionClass.find_all("p",{"data-testid":"vuln-description"})
        removeWordList = ['[<p data-testid="vuln-description">','</p>]'] #Cleaning up the description
        for words in removeWordList:
            getDescription = str(getDescription).replace(words,'')
        #Get the vector string
        getVector = soup.find_all("div",{"class":"col-lg-6 col-sm-12"})
        vector = re.findall("CVSS:\d\.\d\S+",str(getVector))[0] #Using regex to grab the vector string
        #Cleaning and processing the vector string
        vector = vector.replace('</span>','')
        vector = processVector.vectorBreakDown(vector)
        #Finding the CPE String
        findTable = soup.findAll('table',attrs={'data-testid':'vuln-change-history-table'})
        searchSoftwareConfiguration = re.findall("cpe\:\S\.*\S+(?:\s\S+\s\S+\s\S+\s\()?(?:excluding\)|including\))?(?:\s\d+\.\d+)?",str(findTable))
        #Cleaning the CPE String
        for index in range(len(searchSoftwareConfiguration)):
            searchSoftwareConfiguration[index] = searchSoftwareConfiguration[index].replace('</pre>','')
        # Get the solutions table
        solutions_table = soup.find('table', attrs={'data-testid':"vuln-hyperlinks-table"})
        # Get all hyperlinks in solution
        solutions_links = re.findall('(?<=target="_blank">)(.*)(?=</a></td>)', str(solutions_table))
        # Get the CWE table
        CWE_table = soup.find('table', attrs={'data-testid': "vuln-CWEs-table"})
        # Get the CWE-IDs
        CWE_IDs = re.findall('CWE\-\S+', str(CWE_table))[1:]
        # Clean CWE IDs (remove html tags)
        CWE_IDs = [s.replace("</a>", "").replace("</span>", "") for s in CWE_IDs]
        # Get the CWE names
        CWE_Names = re.findall('(?<=vuln-CWEs-link-)(.*)(?=</td>)', str(CWE_table))
        # Clean CWE names(remove first three unwanted chars)
        CWE_Names = [char[3:] for char in CWE_Names]
        # Put CWE IDs and names together in dictionary
        CWE_Dict = {k: v for k, v in zip(CWE_IDs, CWE_Names)}
        if CWE_Dict.get('CWE-917'):
            CWE_Dict['CWE-917'] = "Improper Neutralization of Special Elements used in an Expression Language Statement ('Expression Language Injection')"
        #Appends all the data into a list 
        cvssVersion = vector[0]
        detailsList = [cveNumber.upper(),cvssVersion,cvssScore,getDescription,CWE_Dict]
        for number in range(1,len(vector)):
            detailsList.append(vector[number])
        #Appending the CPE String into the list
        detailsList.append(processCPE.cpeBreakDown(searchSoftwareConfiguration))
        detailsList.append(solutions_links)
        return detailsList
    except:
        message = "No such CVE Record for " + cveNumber.upper()
        print(message)
