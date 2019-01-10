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

def customerloyaltybyyear (unified_table,utable,year):
    year_term = (dt.date(year,1,1),dt.date(year,12,31))
    thisyearpos = unified_table[unified_table.purchase_date >= year_term[0]]
    thisyearpos = thisyearpos[thisyearpos.purchase_date <= year_term[1]]
    registered_thisyear = utable[utable.year == year]
    newuserpos = thisyearpos[thisyearpos.user_id.isin(registered_thisyear.index)]

    active_user_count = len(set(thisyearpos.user_id))
    print ("active customer count for year "+str(year)+" is "+str(active_user_count))

    rem_col = ['user_id','purchase_date']
    day_count = newuserpos.loc[:,rem_col]
    day_count = day_count.sort_values(by = rem_col)
    user_by_days = day_count.groupby('user_id').agg(tb.count_days)

    one_day = user_by_days[user_by_days.purchase_date == 1]
    oneday_count = len(one_day.index)
    print ("only one day user count in year  "+str(year)+" is "+str(oneday_count))
    multi_days = user_by_days[user_by_days.purchase_date > 1]
    multiday_count = len(multi_days.index)
    print ("more than one day user in year "+str(year)+" is "+str(multiday_count))
    regonly = set(registered_thisyear.index)-set(one_day.index) - set(multi_days.index)
    regonly_count = len(regonly)
    print ("reg only count = "+str(regonly_count))
    

    remaining_col = ['user_id','price']
    pricetable = newuserpos.loc[:,remaining_col]
    one_day_table = pricetable[pricetable.user_id.isin(one_day.index)]


    one_day_sales = one_day_table.groupby('user_id').sum()
    oneday_mean = one_day_sales.price.mean()
    print ("one day customer sales mean  "+str(oneday_mean))
    
    multi_day_table = newuserpos[newuserpos.user_id.isin(multi_days.index)]
    multi_day_sales = multi_day_table.groupby('user_id').sum()
    multi_mean = multi_day_sales.price.mean()
    print ("More than one day customer sales mean  "+str(multi_mean))

    return(oneday_count,multiday_count,oneday_mean,multi_mean,regonly_count,active_user_count)

#    user_by_days.loc[:,'visit count'] = 1
#    purchase_count = user_by_days.groupby('purchase_date').sum()
#    purchase_count.to_csv(tb.filepos+"visitcount.csv")
#    print ("visit count is "+str(purchase_count))

if __name__=='__main__':

    allyearpos = tb.postable('unified')
    allyearpos = allyearpos.table
    ut = tb.UserTable('cleanutable')
    utable = ut.usertable

    if utable.index.isnull().any():
        print ("user table has nun user")
    if allyearpos.user_id.isnull().any():
        print ("pos table has nun user")
        nanrows = allyearpos[allyearpos.user_id.isnull()]
        print ("nan rows count is "+str(nanrows.shape[0]))
        print ("nan rows are")
        print (str(nanrows))
        allyearpos = allyearpos.dropna(subset=['user_id'])

    print('user count = '+str(utable.shape[0]))
    utable.loc[:,'year'] = utable.loc[:,'registered_date'].dt.year
    outtable = pd.DataFrame(0,index = [2012,2013,2014,2015,2016,2017],columns = ['only_once','more_than_2','mean_for_once','mean_for_2_or_more','drop_rate','reg_only','reg_only_rate','active_user_count','new_user_ratio'])
#    dic = ['only_once':u'１度のみ','more_than 2':u'複数回','mean_for_once':u'１度のみ購買平均','mean_for_2 or_more':u'複数回購買平均','drop_rate':u'離脱率','reg_only':u'登録のみ','reg_only_rate':u'登録のみ率'])
    for yr in range(2012,2018):
        oneday_count, multiday_count, oneday_mean, multi_mean,regonly ,active_count = customerloyaltybyyear(allyearpos,utable,yr)

        outtable.loc[yr,'only_once'] = oneday_count
        outtable.loc[yr,'more_than_2'] = multiday_count
        outtable.loc[yr,'mean_for_once'] = oneday_mean
        outtable.loc[yr,'mean_for_2_or_more'] = multi_mean
        outtable.loc[yr,'drop_rate'] = float(oneday_count)/float(oneday_count+multiday_count)
        outtable.loc[yr,'reg_only'] = regonly
        outtable.loc[yr,'reg_only_rate'] = float(regonly)/float(oneday_count+multiday_count+regonly)
        outtable.loc[yr,'active_user_count'] = active_count
        outtable.loc[yr,'new_user_ratio'] = (oneday_count+multiday_count)/float(active_count)

#    outtable.rename(columns = dic, inplace = True)
    outtable.to_csv(tb.filepos+"yearldrop.csv")



    

    
