import pandas as pd
import numpy as np

book_name='DataInput2013.xlsx'

wb = pd.ExcelFile(book_name)

## Use sheet names to access sheets
sheet_names=self.wb.sheet_names

## For each item in sheet_names, you can use .columns to quickly access
## The headers, then iterate through those to make sure you have all the data?





