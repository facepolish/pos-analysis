import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import numba
import datetime as dt
import tableclass as tb
from sklearn.decomposition import NMF
from sklearn.preprocessing import normalize
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
from numba import jit


from scipy.spatial import distance
from scipy.cluster import hierarchy

if __name__=='__main__':
    depttable = tb.DEPTtable('HITRMD_DEPT')
    

    pos17= tb.postable(tb.posnamelist[6])
    pos17= pos17.table
    
    ut = tb.UserTable('cleanutable')
    utable = ut.usertable
    print('user count = '+str(utable.shape[0]))
    utable.loc[:,'year'] = utable.loc[:,'registered_date'].dt.year
    
    coutlist = [i for i in range(56)]
    deptprice = pd.DataFrame(0,index = depttable.namedic.keys(),columns = coutlist)
    deptcount = pd.DataFrame(0,index = depttable.namedic.keys(),columns = coutlist)
    
    user17 = utable[utable.year == 2017]
    thisyearpos = pos17[pos17.user_id.isin(user17.index)]
    
    thisyearpos = thisyearpos.sort_values(by = ['user_id','purchase_date'])
    
    usr = 0
    for ind,item in thisyearpos.iterrows():
        if usr != item.user_id:
            #first item
            item_count = 1
            lastdate = item.purchase_date
            usr = item.user_id
        if item.purchase_date.year != lastdate.year or item.purchase_date.month != lastdate.month or item.purchase_date.day != lastdate.day:
            item_count += 1
            lastdate = item.purchase_date
        deptprice.loc[item.DEPT,item_count]+= item.price
        deptcount.loc[item.DEPT,item_count]+= 1
    deptprice = deptprice.rename(index = depttable.namedic)
    deptcount = deptcount.rename(index = depttable.namedic)
    
    deptprice.to_csv(tb.filepos+"visitcountdeptprice.csv")
    deptcount.to_csv(tb.filepos+"visitcountdeptcount.csv")
    
    cross_dept = pd.DataFrame(0,index = depttable.namedic.keys(),columns = depttable.namedic.keys())
    usr = 0
    firstset = set([])
    secondset = set([])
    for ind,item in thisyearpos.iterrows():
        if usr != item.user_id:
            #first item
            for fi in firstset:
                for si in secondset:
                    cross_dept.loc[fi,si]+=1
            item_count = 1
            lastdate = item.purchase_date
            usr = item.user_id
            firstset = set([])
            secondset = set([])
        if item.purchase_date.year != lastdate.year or item.purchase_date.month != lastdate.month or item.purchase_date.day != lastdate.day:
            item_count += 1
            lastdate = item.purchase_date
        if item_count == 1:
            firstset.add(item.DEPT)
        elif item_count == 2:
            secondset.add(item.DEPT)
    cross_dept = cross_dept.rename(index = depttable.namedic,columns = depttable.namedic)
    cross_dept.to_csv(tb.filepos+"crossdept.csv")
        

    
    
