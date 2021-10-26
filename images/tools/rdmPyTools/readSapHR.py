# -*- coding: utf-8 -*-
"""
Created on Thu Feb 11 14:43:28 2021

@author: PieterDV
"""
import pandas as pd
import numpy as np
import re

filename = 'c:\\temp\\sap_hr.csv'
sapHR = pd.read_table(filename, sep='|')
print(sapHR.columns)
#strip [] from column names
sapHR.columns = [name.strip().replace('[', '') for name in sapHR.columns]
sapHR.columns = [name.strip().replace(']', '') for name in sapHR.columns]
#to show all rows/columns in console window
#pd.set_option('display.max_columns', None)
#pd.set_option('display.max_rows', None)
#or, alternatively:
print(sapHR.dtypes.tolist())
print(sapHR.columns.tolist())
for col in sapHR.columns:
    if (re.search("^Generic", col)):
        sapHR.loc[:, col] = sapHR[col].astype(np.object)
print(sapHR.dtypes.tolist())        
#sapHR = sapHR.set_index('Username')
#missing values
missing_value_mask = (sapHR == -999.000)
missing_value_mask.value_counts()
sapHR[missing_value_mask] = np.nan
#iterate over rows
cnt = 1
for row in sapHR.itertuples():
    if (cnt==1):
        print(row.Username, row.Generic01)
    cnt = cnt + 1


