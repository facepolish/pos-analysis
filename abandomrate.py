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
    pos17= tb.postable(tb.posnamelist[6])
    pos17= pos17.table
    pos16= tb.postable(tb.posnamelist[5])
    pos16= pos16.table
    web17 = tb.websalestable(2017)
    web17 = web17.table
    web16 = tb.websalestable(2016)
    web16 = web16.table
    
    ut = tb.UserTable('cleanutable')
    utable = ut.usertable
    print('user count = '+str(utable.shape[0]))
    utable.loc[:,'year'] = utable.loc[:,'registered_date'].dt.year
#    utable.year = utable.registered_date.dt.year

    remaining_col = ['gender','year']
    print ("utable columns = "+str(utable.columns))
    year_ana = utable.loc[:,remaining_col]
    regyear = utable.groupby('year').count()
    rendic = {'gender':u'年加入数'}
    regyear = regyear.rename(columns = rendic)
    regyear.to_csv(tb.filepos+"yearlyreg.csv")

    term56 = (dt.date(2016,12,1),dt.date(2017,11,30))
    
    utable56 = utable[utable.registered_date>=term56[0]]
    utable56 = utable56[utable56.registered_date<=term56[1]]
    print('56 user count = '+str(utable56.shape[0]))

    pos17 = pos17[pos17.purchase_date>=term56[0]]
    pos17 = pos17[pos17.purchase_date<=term56[1]]

    pos16 = pos16[pos16.purchase_date>=term56[0]]
    pos16 = pos16[pos16.purchase_date<=term56[1]]

    web17 = web17[web17.purchase_date>=term56[0]]
    web17 = web17[web17.purchase_date<=term56[1]]

    web16 = web16[web16.purchase_date>=term56[0]]
    web16 = web16[web16.purchase_date<=term56[1]]

    
    unified_table = pos16
    unified_table = unified_table.append(pos17)
    unified_table = unified_table.append(web17)
    unified_table = unified_table.append(web16)
    unified_table = unified_table[unified_table.user_id.isin(utable56.index)]

    remaining_col = ['user_id','purchase_date']
    datetable = unified_table.loc[:,remaining_col]
    
    user_by_days = datetable.groupby('user_id').agg(tb.count_days)

    one_day = user_by_days[user_by_days.purchase_date == 1]
    print ("only one day user count = "+str(len(one_day.index)))
    multi_days = user_by_days[user_by_days.purchase_date > 1]
    print ("more than one day user count = "+str(len(multi_days.index)))
    regonly = set(utable56.index)-set(one_day.index) - set(multi_days.index)
    print ("reg only count = "+str(len(regonly)))
    

    remaining_col = ['user_id','price']
    pricetable = unified_table.loc[:,remaining_col]
    one_day_table = pricetable[pricetable.user_id.isin(one_day.index)]


    one_day_sales = one_day_table.groupby('user_id').sum()
    print ("one day customer sales mean  "+str(one_day_sales.price.mean()))
    
    multi_day_table = unified_table[pricetable.user_id.isin(multi_days.index)]
    multi_day_sales = multi_day_table.groupby('user_id').sum()
    print ("More than one day customer sales mean  "+str(multi_day_sales.price.mean()))

    user_by_days.loc[:,'visit count'] = 1
    purchase_count = user_by_days.groupby('purchase_date').sum()
    purchase_count.to_csv(tb.filepos+"visitcount.csv")
    print ("visit count is "+str(purchase_count))
    

    
    

