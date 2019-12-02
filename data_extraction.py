import json
import csv
import sys,codecs,locale
import pandas as pd


if sys.stdout.encoding != 'UTF-8':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
if sys.stderr.encoding != 'UTF-8':
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

wordFreqDic = {}
subwordFreqDic = {}


def Write_file(file,output_file):
    with open(file, "r") as read_file:
        data = json.load(read_file)

    strAttribute="'"
    for key, value in data.items():
        subdate = value

    for attribute, value in subdate.items() :
        strAttribute+=attribute
        strAttribute+="',"
        strAttribute+="'"
        
    newStrAttribute = strAttribute[:-2]

    with open(output_file, mode='w',encoding='utf=8') as csv_file:
        fieldnames = ['report-url', 'accidnet-classification', 'location', 'mine-type', 'mine-controller', 'mined-mineral','incident-date','public-notice','preliminary-report','fatality-alert','final-report']
        #fieldnames = [newStrAttribute]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for key, value in data.items():
        	writer.writerow(value)


def RemoveBlankLine_file(file):
    try:
        file_object = open(file, 'r',encoding='utf=8')
        lines = csv.reader(file_object, delimiter=',', quotechar='"')
        flag = 0
        data=[]
        for line in lines:
            if line == []:
                flag =1
                continue
            else:
                data.append(line)
        file_object.close()
        if flag ==1: #if blank line is present in file
            file_object = open(file, 'w',encoding='utf=8')
            for line in data:
                str1 = ','.join(line)
                file_object.write(str1+"\n")
            file_object.close() 
    except Exception as e:
        print(e)    


def Enrichment_file(file,final_file):
    df = pd.read_csv(file)
    #checking the number of empty rows in th csv file
    print (df.isnull().sum())
    #Droping the empty rows
    modifiedDF = df.dropna()
    #Saving it to the csv file 
    modifiedDF.to_csv(final_file,index=False)

def main():
    input_file='report_info.json'
    documents_path='fatality-alert.csv'
    final_file = 'final_Report.csv'
    Write_file(input_file,documents_path)
    Enrichment_file(documents_path,final_file)


if __name__ == '__main__':
    main()       