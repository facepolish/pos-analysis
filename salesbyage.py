import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime
import os
import numba
import datetime as dt
import tableclass as tb
from scipy.spatial.distance import correlation
def ItemByYear (table,item,dept):
    deptname = dept.namedic[item]
    shoebuyers = table[table.DEPT == item]
    yearly_corr = pd.pivot_table(shoebuyers,index = 'user_id',columns = 'year',values = 'price',aggfunc = 'sum').fillna(0)
    cor_mat = yearly_corr.corr()
    cor_mat.to_csv(tb.filepos+'YearlyCorr'+deptname+'.csv')

def BrandByYear (table,brand_name):
    shoebuyers = table[table.brand == brand_name]
    yearly_corr = pd.pivot_table(shoebuyers,index = 'user_id',columns = 'year',values = 'price',aggfunc = 'sum').fillna(0)
    cor_mat = yearly_corr.corr()
    cor_mat.to_csv(tb.filepos+'YearlyCorr'+brand_name+'.csv')

def BrandByMonth (table,brand_name):
    shoebuyers = table[table.brand == brand_name]
    yearly_corr = pd.pivot_table(shoebuyers,index = 'user_id',columns = 'month',values = 'price',aggfunc = 'sum').fillna(0)
    cor_mat = yearly_corr.corr()
    cor_mat.to_csv(tb.filepos+'MonthlyCorr'+brand_name+'.csv')

if __name__=='__main__':
    depttable = tb.DEPTtable('HITRMD_DEPT')

    ut = tb.UserTable('cleanutable')
    utable = ut.usertable
    posall = tb.postable('unified').table
    posall.loc[:,'user_id'] = posall.loc[:,'user_id'].astype('str')
    posall = posall[posall.user_id.isin(utable.index)]
    posall.loc[:,'year'] = list( map((lambda x: x.year), posall.purchase_date))
    posall.loc[:,'month'] = list( map((lambda x: x.month), posall.purchase_date))
#    posall.loc[:,'age'] = list( map((lambda x,y : (utable.loc[x,'age'] + y - 2017)),posall.user_id, posall.year ))
#    purchae_table = pd.pivot_table(posall,index = 'age',columns = 'year',values = 'price',aggfunc = 'sum').fillna(0)
#    purchae_table.to_csv(tb.filepos+'salesByAgeAndYear.csv')
    
    yearly_corr = pd.pivot_table(posall,index = 'user_id',columns = 'year',values = 'price',aggfunc = 'sum').fillna(0)
    cor_mat = yearly_corr.corr()
    cor_mat.to_csv(tb.filepos+'YearlyCorr.csv')
    serial_buyers = yearly_corr[(yearly_corr.loc[:,2011] > 50000)]
    serial_buyers = serial_buyers[(yearly_corr.loc[:,2012] > 50000)]
    print ("number of serial buyers = "+str(serial_buyers.shape[0]))
    print ("total purchase of 2015 is "+str(serial_buyers.loc[:,2015].mean()))
    print ("total purchase of 2016 is "+str(serial_buyers.loc[:,2016].mean()))
    print ("total purchase of 2017 is "+str(serial_buyers.loc[:,2017].mean()))
    ser_cor_mat = serial_buyers.corr()
    ser_cor_mat.to_csv(tb.filepos+'SerialCorr.csv')

    pos2017 = posall[posall.year == 2017]
    monthly_corr = pd.pivot_table(posall,index = 'user_id',columns = 'month',values = 'price',aggfunc = 'sum').fillna(0)
    cor_mat = monthly_corr.corr()
    cor_mat.to_csv(tb.filepos+'MonthlyCorr.csv')
    
    for key in depttable.namedic:
        ItemByYear(posall,key,depttable)
    
    brandlist = list(set(posall.brand))

    for key in brandlist:
        BrandByYear(posall,key)

    for key in brandlist:
        BrandByMonth(pos2017,key)

#    shoebuyers = posall[posall.DEPT == 1]
#    yearly_corr = pd.pivot_table(shoebuyers,index = 'user_id',columns = 'year',values = 'price',aggfunc = 'sum').fillna(0)
#    cor_mat = yearly_corr.corr()
#    cor_mat.to_csv(tb.filepos+'YearlyCorrShoe.csv')

    low_rank = [u'1合目登頂中',]

    middle_to_high = [u'登頂達成！', u'6合目登頂中', u'4合目登頂中',  u'8合目登頂中']
#    user_ranks = set(utable.user_rank)
#    print ("user_rank = "+str(user_ranks))
    roku = utable[utable.user_rank.isin(middle_to_high)]
    posroku = posall[posall.user_id.isin(roku.index)]
    yearly_corr = pd.pivot_table(posroku,index = 'user_id',columns = 'year',values = 'price',aggfunc = 'sum').fillna(0)
    cor_mat = yearly_corr.corr()
    cor_mat.to_csv(tb.filepos+'YearlyCorrYon.csv')

    middle_to_high = [u'登頂達成！', u'6合目登頂中',  u'8合目登頂中']
#    user_ranks = set(utable.user_rank)
#    print ("user_rank = "+str(user_ranks))
    roku = utable[utable.user_rank.isin(middle_to_high)]
    posroku = posall[posall.user_id.isin(roku.index)]
    yearly_corr = pd.pivot_table(posroku,index = 'user_id',columns = 'year',values = 'price',aggfunc = 'sum').fillna(0)
    cor_mat = yearly_corr.corr()
    cor_mat.to_csv(tb.filepos+'YearlyCorrRoku.csv')

    middle_to_high = [u'登頂達成！', u'8合目登頂中']
#    user_ranks = set(utable.user_rank)
#    print ("user_rank = "+str(user_ranks))
    roku = utable[utable.user_rank.isin(middle_to_high)]
    posroku = posall[posall.user_id.isin(roku.index)]
    yearly_corr = pd.pivot_table(posroku,index = 'user_id',columns = 'year',values = 'price',aggfunc = 'sum').fillna(0)
    cor_mat = yearly_corr.corr()
    cor_mat.to_csv(tb.filepos+'YearlyCorrHachi.csv')
    


    '''
    check_brand_list = [u'ノースフェイス',u'デサント',u'ローバー',u'スノーピーク',]
    year_list = [2011,2012,2013,2014,2015,2016,2017]
    
    for br in check_brand_list:
        br_purchase = posall[posall.brand == br]
        y_users = []
        for y in year_list:
            y_table = br_purchase[br_purchase.year == y]
            y_users.append(set(y_table.user_id))

        setoflen = len(y_users)
        uset2 = []
        for i in range(setoflen):
            uset = set([])
            for j in range(setoflen):
                if j != i:
                    uset = uset | y_users[j]
            uset2.append(uset)
        retset = set([])
        for i in range(setoflen):
            intersec = (y_users[i] & uset2[i])
            retset = retset | intersec
        double_purchasers = br_purchase[br_purchase.user_id.isin(retset)]
        yearly_corr = pd.pivot_table(double_purchasers,index = 'user_id',columns = 'year',values = 'price',aggfunc = 'sum').fillna(0)
        cor_mat = yearly_corr.corr()
        cor_mat.to_csv(tb.filepos+'YearlyCorr'+br+'.csv')
    '''
        
            


