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
    table2 = pd.read_pickle('C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/bi/data/bi/pos.pkl')
    '''
    table = pd.read_pickle('E:/download/pos.pkl')
    table3 = pd.read_pickle('J:/Kobe results/workspace/Kojitsu/src/bisite/bi/data/bi/pos.pkl')
    table4 = pd.read_pickle('J:/Kobe results/workspace/Kojitsu/src/bisite/temppos.pkl')
    table5 = pd.read_pickle('J:/Kobe results/workspace/Kojitsu/src/bisite/outpos.pkl')
    
    table4.cost = table4.cost.fillna(0)
    table4 = posaddcols(table4)
    table4.to_pickle(table5)
    '''
    collen = len(table2.columns)
    print ("num of col = "+str(collen))
    print (table2.columns)
