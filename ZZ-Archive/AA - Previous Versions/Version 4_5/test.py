from openpyxl import Workbook
from openpyxl import load_workbook

path = "/home/wantsomechocolate/Code/EnergyAnalysis/Sample Input/Data Input One Month.xlsx"
wb = load_workbook(path)
print "loaded workbook"
sheet = wb.get_sheet_by_name('Interval Temp')
print "got sheet"
sheet_data_range = sheet.columns
print "got the cell addresses"
sheet_data=[]
for i in range(len(sheet_data_range)):
    sheet_data.append([])
    
