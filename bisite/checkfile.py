import pandas as pd
import pickle
from scipy.sparse import csr_matrix
from pandas.api.types import CategoricalDtype
from sklearn.decomposition import NMF
import numpy as np
import os
#from .posenv import uservecfile,itemvecfile,posfile,deptuserfile,sdeptvecfile,sdeptuserfile,samecartitemvecfile,deptvecfile,depttablefile


import numpy as np
import math
from sklearn.preprocessing import normalize

if __name__=='__main__':
    table = pd.read_pickle('E:/download/pos.pkl')
    table2 = pd.read_pickle('C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/bi/data/bi/pos.pkl')
    table3 = pd.read_pickle('J:/Kobe results/workspace/Kojitsu/src/bisite/bi\data/bi/pos.pkl')

#    tables = table2.sort_values(by="slip_id")
    # check date range
    min_date = min(table.purchase_date)
    max_date = max(table.purchase_date)
    min_date2 = min(table2.purchase_date)
    max_date2 = max(table2.purchase_date)
    hight = table.shape[0]
    hight2 = table2.shape[0]
    print ("min date is "+str(min_date))
    print ("max date is "+str(max_date))
    print ("record count is "+str(hight))

    print ("min date is "+str(min_date2))
    print ("max date is "+str(max_date2))
    print ("record count is "+str(hight2))

    table_firstday = table[table.purchase_date == min_date]
    print ("count of first day is "+str(table_firstday.shape[0]))
    table_firstday2 = table2[table2.purchase_date == min_date]
    table_firstday3 = table3[table3.purchase_date == min_date]
    print ("count of first day is "+str(table_firstday2.shape[0]))
    print ("count of first day is "+str(table_firstday3.shape[0]))
    table_firstday = table_firstday.sort_values(by="purchase_time")
    table_firstday2 = table_firstday2.sort_values(by="purchase_time")
    table_firstday3 = table_firstday3.sort_values(by="purchase_time")
    table_firstday.to_excel('E:/download/pos.xlsx')
    table_firstday2.to_excel('E:/download/pos2.xlsx')
    table_firstday3.to_excel('E:/download/pos3.xlsx')

