import csv, os
def write_tofile(detailsList,csvName):
    header = ['Group Name','CVE','CVSS Version','Severity','Description','Weakness Enumeration','Attack Vector','Attack Complexity','Privileges Required','User Interaction','Confidentiality','Integrity','Availability','CPE String','Advisories/Solutions/Tools']    
    dataList = []
    try:
        for i in range(len(detailsList)):
            dataList.append(detailsList[i])
        separator = ','
        headerCheck = separator.join(header) 
        if not csvName.endswith('.csv'):
            csvName = csvName + '.csv'
        if not os.path.exists(csvName):
            newFile = open(csvName, "w")
            newFile.close()
        with open(csvName, 'r+', newline='') as fileWrite:
            content = fileWrite.read()
            if headerCheck in content:
                writer=csv.writer(fileWrite)
                writer.writerow(dataList)
            else:
                writer=csv.writer(fileWrite)
                writer.writerow(header) 
                writer.writerow(dataList)
        fileWrite.close()
    except:
        pass
