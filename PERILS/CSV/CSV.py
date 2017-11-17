import csv


class CSV:
    csvURL = None
    columnDict = None
    rowDict = None

    def __init__(self, csvURL, columnDict, rowsDict):
        self.csvURL = csvURL
        self.columnDict = columnDict
        self.rowDict = rowsDict

    def outputCSVFile(self):
        with open(self.csvURL, 'w', newline='') as csvFile:
            writer = csv.DictWriter(csvFile, fieldnames=self.columnDict)
            writer.writeheader()
            writer.writerows(self.rowDict)
        csvFile.close()
