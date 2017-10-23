import csv

# TODO
def addEmptyColumns(header, num):
    for i in range(num):
        header.append("")
    return header

def MergeTwoCSV(csv1, csv2):
    with open(csv1, newline='') as file1:
        r = csv.reader(file1)
        data = [line for line in r]

    # Create headers for the final table
    with open(csv2, 'w', newline='') as file2:
        w = csv.writer(file2)
        header = ["PERILS6", "PERILS12", "PERILS11", "PRMergedByNonGithub"]
        header = addEmptyColumns(header, 4)
        header.append("PERILS3")
        header = addEmptyColumns(header, 4)
        header.append("PERILS16")
        header = addEmptyColumns(header, 4)
        header.append("PERILS7")
        header = addEmptyColumns(header, 4)
        header.append("PERILS2")
        w.writerow(header)
        w.writerows(data)

MergeTwoCSV("./output/table.csv", "./output/table.csv")