import os
import pandas as pd
import numpy
import datetime
import hashlib
import csv
import gc
import math
import tqdm
import os.path
import matplotlib.pyplot as plt
from numba import jit
from django.conf import settings
from posenv import colnamedic,col_dtype,kojitsupath,gradedic


filepos = os.path.join(kojitsupath,'output/')
fileinputpos = os.path.join(kojitsupath,'input/')
ext = '.csv'



class DEPTtable (object):
    def __init__(self,filename):
        absfile=filename
        if not(os.path.exists(absfile)):
            absfile = fileinputpos+filename+ext
        
        self.depttable = pd.read_csv(absfile,encoding = 'CP932')
        self.uniqdept = pd.Series.unique(self.depttable.DEPT)
        self.depttable.rename(columns=colnamedic, inplace=True)

        self.namedic = {}
        self.subdic = {}
        for dept in self.uniqdept:
            thisdept = self.depttable[self.depttable.DEPT==dept].dropna(axis=1)
            thisdept = thisdept.dropna()
            print (thisdept)
            categorynames = thisdept.category
            categoryname = categorynames.iloc[0]
            self.namedic[dept]=categoryname
            subdic={}
            maxj = thisdept.shape[0]
            for j in range(maxj):
                subdic[thisdept.SDEPT.iloc[j]] = thisdept.item_code1.iloc[j]
            self.subdic[dept] = subdic
        
    def DEPT_NO_to_string(self,deptid):
        return(self.namedic[deptid])

class UserTable(object):

    def __init__(self,filename):
        absfile=filename
        if not(os.path.exists(absfile)):
            absfile = fileinputpos+filename+ext
        self.usertable = pd.read_csv(absfile,encoding = 'CP932',dtype = col_dtype)
        self.usertable = self.usertable.set_index('user_id')
        self.usertable.age = self.usertable.age.fillna(0)
        self.usertable.registered_date = pd.to_datetime( self.usertable.registered_date,format = '%Y%m')
#        self.ranklist = pd.Series.unique(self.usertable.rank)
        self.regyearlist = pd.Series.unique(self.usertable.registered_date.dt.year)
        print(self.usertable.head(5))
        
    def CheckRegistration(self,user):
        if (user in self.usertable.index):
            self.currentuser = self.usertable.loc[user]
            return(True)
        else :
            return(False)

    def GetAge(self,user):
        if (user in self.usertable.index):
            return(self.usertable.loc[user].age)
        else :
            return(0)
    def RegYear(self,user):
        if (user in self.usertable.index):
            regdate = self.usertable.loc[user].registered_date
            regyear = regdate[:4]
            return(int(regyear))
        return(0)
            

class itemsalestable(object):
    def __init__(self,filename):
        absfile=filename
        if not(os.path.exists(absfile)):
            absfile = fileinputpos+filename+ext
        datatable = pd.read_csv(absfile,encoding = 'CP932',dtype = col_dtype)
        datatable.rename(columns = colnamedic, inplace = True)
        datatable.user_id = datatable.user_id.astype(str)
        datatable.purchase_date = pd.to_datetime(datatable.purchase_date,format = '%Y/%m/%d')
        datatable.purchase_time = pd.to_datetime(datatable.purchase_time,format = '%H%M%S')

        self.table = datatable
        
def posaddcols(postable):
    postable.loc[:, 'itemid'] = postable.brand + postable.type + postable.item_name
    postable.loc[:, 'unit_price'] = postable.price / postable.amount
    weeks = [str(x.isocalendar()[0]) + ' ' + str(x.isocalendar()[1]).rjust(2) for x in postable.purchase_date]
    postable.loc[:, 'year_week'] = weeks
    return(postable)

class postable(itemsalestable):
    def __init__(self,filename):
        super(postable,self).__init__(filename)
        self.prefix = 'pos'

def postable2():
    path1= fileinputpos+"57期分析用資料/実店舗/"
    file1="会員購買履歴_57期一四半期.xlsx"
    file2="会員購買履歴_57期二四半期.xlsx"
    file3 = "会員購買履歴_57期三四半期.xlsx"
    file4 = "会員購買履歴_57期四四半期.xlsx"
    filelist = [file1,file2,file3,file4]

    file5 = "商品マスタ.xlsx"
    file6 = "HITRMD_ﾒｰｶｰｺｰﾄﾞ.xlsx"

    path2 = fileinputpos+"メーカーコード・商品マスタ/"
    iterm_master = pd.read_excel(path2+file5,dtype=col_dtype)
    iterm_master.rename(columns=colnamedic,inplace=True)
    iterm_master = iterm_master[['jan_code','DEPT','SDEPT','cost']]
    maker_code = pd.read_excel(path2+file6,dtype=col_dtype)
    maker_code.rename(columns=colnamedic,inplace=True)
    maker_code = maker_code[['maker_code','brand']]

    pos = pd.read_excel(path1+file1,dtype=col_dtype)
    for fil in filelist[1:]:
        pos1 = pd.read_excel(path1 + fil, dtype=col_dtype)
        pos = pos.append(pos1)
    pos.rename(columns=colnamedic,inplace=True)
#    pos.rename(columns=colnamedic_pos,inplace=True)


    pos = pd.merge(pos,iterm_master , on ='jan_code')
    pos = pd.merge(pos,maker_code ,on ='maker_code')
    pos.purchase_date = pd.to_datetime(pos.purchase_date,format = '%Y%m%d')
    pos.purchase_time = pd.to_datetime(pos.purchase_time,format = '%H%M%S')
    pos.user_id = pos.user_id.astype(str)
    col_list = list(set(pos.columns) & set(colnamedic.values()))
    pos = pos[col_list]
    return(pos)
    

def getallpos(pos=None):
    pos1 = postable('unified').table
    latest_date = max(pos1.purchase_date)
    pos2 = postable2()
    pos2 = pos2[pos2.purchase_date>latest_date]
    pos1 = pos1.append(pos2)
    pos1.cost = pos1.cost.fillna(0)
    pos1.cost = pos1.cost.astype('int')
    pos1 = posaddcols(pos1)

    return(pos1)

def usertable2():
    path3 = fileinputpos+"57期分析用資料\WebShop\顧客/"
    file7 = "customer190124最新.xlsx"
    customers = pd.read_excel(path3+file7,dtype=col_dtype)
    customers.rename(columns=colnamedic,inplace=True)
    customers.birth_year_month = pd.to_datetime(customers.birth_year_month,format = '%Y/%m')
    customers.user_id = customers.user_id.astype(str)
    year = datetime.timedelta(days=365)
    customers.loc[:,'age'] = [(datetime.datetime(2017,1,1) - x)//year for x in customers.birth_year_month]
    col_list = list(set (customers.columns) & set(colnamedic.values()))
    customers = customers[col_list]
    customers = customers.set_index('user_id')
    return(customers)

def getallusers(user=None):
    user1 = UserTable('cleanutable').usertable
    user2 = usertable2()
    setuser1 = set(user1.index)
    setuser2 = set(user2.index)
    intersec = setuser1 & setuser2
    user1only = setuser1 - intersec
    user1 = user1[user1.index.isin(user1only)]
    user1 = user1.append(user2)
    user1.user_rank = user1.user_rank.replace(gradedic)
    return(user1)

