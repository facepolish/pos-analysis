from bi.posenv import depttablefile
import matplotlib.pyplot as plt
import pandas as pd
from datetime import timedelta,datetime,date
from numba import jit

posfile = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/bi/data/bi/pos.pkl'
userfile = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/bi/data/bi/user.pkl'
outfile = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/fands.xlsx'
outpath = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/'




if __name__=='__main__':

    depdic = pd.read_pickle(depttablefile)

    postable = pd.read_pickle(posfile)
    postable = postable.reset_index()
    user = pd.read_pickle(userfile)
    user = user.reset_index()
    totalusercount = len(set(user.user_id))
    morethan10 = user[user.visit_count>=8]
    morethan10count = len(set(morethan10.user_id))
    print ("more than 10 ratio = "+str(morethan10count/totalusercount))
    begindate = pd.Timestamp(2019,6,1)
    enddate =  pd.Timestamp(2019,6,30)
    postable = postable[postable.purchase_date>=begindate]
    postable = postable[postable.purchase_date <=enddate]

    postable = pd.merge(postable,user,on='user_id')
    postable = postable[['visit_count','price']]
    
    sales_by_count = postable.groupby("visit_count").agg('sum')
    sales_by_count.to_excel(outpath+'salesbycount.xlsx')



    '''
    begindate = pd.Timestamp(2018,12,1)
    enddate =  pd.Timestamp(2019,11,30)
    target_users = user[user.registered_date>=begindate]
    target_users = target_users[target_users.registered_date<=enddate]
    pos_target = postable[postable.user_id.isin(target_users.user_id)]

    ret_table = set_freq(pos_target)
    userbybrandprice = pd.pivot_table(ret_table, index='visit_count', columns='brand', values='price', aggfunc='sum').fillna(0)
    userbyDEPTprice = pd.pivot_table(ret_table, index='visit_count', columns='DEPT', values='price', aggfunc='sum').fillna(0)

    userbybrandcount = pd.pivot_table(ret_table, index='visit_count', columns='brand', values='count', aggfunc='sum').fillna(0)
    userbyDEPTcount = pd.pivot_table(ret_table, index='visit_count', columns='DEPT', values='count', aggfunc='sum').fillna(0)
    userbyDEPTprice.columns = [int(x) for x in userbyDEPTprice.columns]
    userbyDEPTcount.columns = [int(x) for x in userbyDEPTcount.columns]
    userbyDEPTprice = userbyDEPTprice.rename(columns=depdic)
    userbyDEPTcount = userbyDEPTcount.rename(columns=depdic)

    userbybrandprice.to_excel(outpath+'brandprice1.xlsx')
    userbybrandcount.to_excel(outpath+'brandcount1.xlsx')
    userbyDEPTprice.to_excel(outpath+'deptprice1.xlsx')
    userbyDEPTcount.to_excel(outpath+'deptcount1.xlsx')


    begindate = pd.Timestamp(2017,12,1)
    enddate =  pd.Timestamp(2018,11,30)
    target_users = user[user.registered_date>=begindate]
    target_users = target_users[target_users.registered_date<=enddate]
    pos_target = postable[postable.user_id.isin(target_users.user_id)]

    ret_table = set_freq(pos_target)
    userbybrandprice = pd.pivot_table(ret_table, index='visit_count', columns='brand', values='price', aggfunc='sum').fillna(0)
    userbyDEPTprice = pd.pivot_table(ret_table, index='visit_count', columns='DEPT', values='price', aggfunc='sum').fillna(0)

    userbybrandcount = pd.pivot_table(ret_table, index='visit_count', columns='brand', values='count', aggfunc='sum').fillna(0)
    userbyDEPTcount = pd.pivot_table(ret_table, index='visit_count', columns='DEPT', values='count', aggfunc='sum').fillna(0)
    userbyDEPTprice.columns = [int(x) for x in userbyDEPTprice.columns]
    userbyDEPTcount.columns = [int(x) for x in userbyDEPTcount.columns]
    userbyDEPTprice = userbyDEPTprice.rename(columns=depdic)
    userbyDEPTcount = userbyDEPTcount.rename(columns=depdic)

    userbybrandprice.to_excel(outpath+'brandprice2.xlsx')
    userbybrandcount.to_excel(outpath+'brandcount2.xlsx')
    userbyDEPTprice.to_excel(outpath+'deptprice2.xlsx')
    userbyDEPTcount.to_excel(outpath+'deptcount2.xlsx')


    begindate = pd.Timestamp(2018,12,1)
    enddate =  pd.Timestamp(2019,11,30)
    pos_target = postable[postable.purchase_date>=begindate]
    pos_target = pos_target[pos_target.purchase_date<=enddate]

    ret_table = set_freq(pos_target)
    userbybrandprice = pd.pivot_table(ret_table, index='visit_count', columns='brand', values='price', aggfunc='sum').fillna(0)
    userbyDEPTprice = pd.pivot_table(ret_table, index='visit_count', columns='DEPT', values='price', aggfunc='sum').fillna(0)

    userbybrandcount = pd.pivot_table(ret_table, index='visit_count', columns='brand', values='count', aggfunc='sum').fillna(0)
    userbyDEPTcount = pd.pivot_table(ret_table, index='visit_count', columns='DEPT', values='count', aggfunc='sum').fillna(0)
    userbyDEPTprice.columns = [int(x) for x in userbyDEPTprice.columns]
    userbyDEPTcount.columns = [int(x) for x in userbyDEPTcount.columns]
    userbyDEPTprice = userbyDEPTprice.rename(columns=depdic)
    userbyDEPTcount = userbyDEPTcount.rename(columns=depdic)

    userbybrandprice.to_excel(outpath+'brandprice3.xlsx')
    userbybrandcount.to_excel(outpath+'brandcount3.xlsx')
    userbyDEPTprice.to_excel(outpath+'deptprice3.xlsx')
    userbyDEPTcount.to_excel(outpath+'deptcount3.xlsx')
    begindate = pd.Timestamp(2017,12,1)
    enddate =  pd.Timestamp(2018,11,30)
    pos_target = postable[postable.purchase_date>=begindate]
    pos_target = pos_target[pos_target.purchase_date<=enddate]

    ret_table = set_freq(pos_target)
    userbybrandprice = pd.pivot_table(ret_table, index='visit_count', columns='brand', values='price', aggfunc='sum').fillna(0)
    userbyDEPTprice = pd.pivot_table(ret_table, index='visit_count', columns='DEPT', values='price', aggfunc='sum').fillna(0)

    userbybrandcount = pd.pivot_table(ret_table, index='visit_count', columns='brand', values='count', aggfunc='sum').fillna(0)
    userbyDEPTcount = pd.pivot_table(ret_table, index='visit_count', columns='DEPT', values='count', aggfunc='sum').fillna(0)
    userbyDEPTprice.columns = [int(x) for x in userbyDEPTprice.columns]
    userbyDEPTcount.columns = [int(x) for x in userbyDEPTcount.columns]
    userbyDEPTprice = userbyDEPTprice.rename(columns=depdic)
    userbyDEPTcount = userbyDEPTcount.rename(columns=depdic)

    userbybrandprice.to_excel(outpath+'brandprice4.xlsx')
    userbybrandcount.to_excel(outpath+'brandcount4.xlsx')
    userbyDEPTprice.to_excel(outpath+'deptprice4.xlsx')
    userbyDEPTcount.to_excel(outpath+'deptcount4.xlsx')
    '''





