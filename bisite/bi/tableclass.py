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
from numba import jit
from django.conf import settings
from sqlalchemy import create_engine
from datetime import timedelta
import contextlib
from .posenv import col_dtype,colnamedic,possource_columns,usersource_columns,possource_dbname,possource_datecolmns,usersource_dbname,kojitsupath,gradedic,db_settings,DB_OFFLINE,itemdbfile


filepos = os.path.join(kojitsupath,'output/')
fileinputpos = os.path.join(kojitsupath,'input/')
ext = '.csv'

from_sql=True

def col_str (lis):
    st = ''
    for i in range(0,len(lis)-1):
        st = st+lis[i]+','
    st=st+lis[len(lis)-1]
    return (st)

@contextlib.contextmanager
def db_conn():
    try:
        os.environ['NLS_LANG'] = 'JAPANESE_JAPAN.UTF8'
        engine = create_engine("oracle://{user}:{password}@{host}:{port}/{database}".format(**db_settings) ,echo=True)
        connection = engine.connect()
#        result = connection.execute("ALTER SESSION SET CURRENT_SCHEMA=HITRMD")
#        result = connection.execute("alter session set container=posdata")
        yield connection
    finally:
        connection.close()

def prev_dat(d):
    day_before_max = d - timedelta(days=1)
    day_string = day_before_max.strftime("%Y/%m/%d")
    return(day_string)

def convert_table(table):
    for col in table.columns:
        ty = col_dtype.get(col,0)
        if not (ty == 0):
            table.loc[:,col] = table.loc[:,col].astype(ty)
    return(table)

class itemdb():
    if os.path.exists(itemdbfile):
        item_tableold = pd.read_pickle(itemdbfile)
    if DB_OFFLINE:
        item_table = item_tableold
    else:
        with db_conn() as connection:
            item_master_cols = ['JANｺｰﾄﾞ','DEPT','S_DEPT','ﾒｰｶｰｺｰﾄﾞ','商品名_漢字','原価']
            item_sql_string = "SELECT {item_cols} FROM HITRMD.商品マスタ".format(item_cols=col_str(item_master_cols))
            item_table = pd.read_sql(item_sql_string,connection)
            item_table = item_table.rename(columns = colnamedic)
            maker_code_cols = ['ﾒｰｶｰｺｰﾄﾞ','ﾒｰｶｰ名_漢字']
            maker_code_sql_string = "SELECT  {maker_code_cols} FROM HITRMD.ﾒｰｶｰｺｰﾄﾞ".format(maker_code_cols=col_str(maker_code_cols))
            maker_code_table = pd.read_sql(maker_code_sql_string,connection)
            maker_code_table = maker_code_table.rename(columns = colnamedic)
            item_table = pd.merge(item_table,maker_code_table,on='maker_code',how='left')
        item_table = convert_table(item_table)
        item_table = item_table.set_index('jan_code')
        dif_ind = set(item_tableold.index) - set(item_table.index)
        item_tableold = item_tableold[item_tableold.index.isin(dif_ind)]
        item_table = item_table.append(item_tableold)
        item_table.to_pickle(itemdbfile)
    @classmethod
    def getitemdb(cls):
        return(cls.item_table)

def getposdb(posdb=None,max_rep=10,update = False):
    base_string = "select {pos_col} from {table_name} ".format(pos_col=col_str(possource_columns),table_name = possource_dbname) #
    order_by = " ORDER BY 売上伝票番号 "
    row_limit = "ROWNUM<=100000 "

    outframe = pd.DataFrame(columns  = possource_columns)
    outframe = outframe.rename(columns = colnamedic)

    if update==False:
        last_receit = 0
    else:
        last_receit = max(posdb.slip_id)
        print ("last slit_id is "+posdb.slip_id)
    item_table = itemdb.getitemdb()
    with db_conn() as connection:
        for i in range(max_rep):
            if not(last_receit == 0):
                limit_items =  " WHERE 売上伝票番号 > {lastreceit_id} AND ".format (lastreceit_id = str(last_receit))
            else:
                limit_items = "WHERE "
            pos_sql_string = base_string+limit_items+row_limit
            sqlpos = pd.read_sql(pos_sql_string,connection,parse_dates = possource_datecolmns)
            sqlpos = sqlpos.rename(columns = colnamedic)
            print (sqlpos.head())
            if sqlpos.shape[0]==0:
                break
            else:
                outframe = outframe.append(sqlpos)
                last_receit = max(outframe.slip_id)
        item_table_merge = item_table.reset_index()
        outframe = pd.merge(outframe,item_table_merge,on='jan_code',how='inner')

        print (item_table.head())
#    outframe = posaddcols(outframe)
    outframe = convert_table(outframe)

    return(outframe)

def getuserdb():# user database always should be downloaded
    user_sql_string = "select {user_col} from {table_name}".format(user_col=col_str(usersource_columns),table_name=usersource_dbname)
    with db_conn() as connection:
        sqluser = pd.read_sql(user_sql_string,connection)
    sqluser = sqluser.rename(columns = colnamedic)
    sqluser = convert_table(sqluser)
    return(sqluser)

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
#    postable.loc[:, 'itemid'] = postable.brand + str(postable.type) + postable.item_name
    postable.amount = postable.amount.replace(0,1) #avoid inf error
    postable.loc[:, 'unit_price'] = postable.price / postable.amount
    weeks = [str(x.isocalendar()[0]) + ' ' + str(x.isocalendar()[1]).rjust(2) for x in postable.purchase_date]
    postable.loc[:, 'year_week'] = weeks
    postable.loc[:,'user_id'] = [x[0:12] for x in postable.loc[:,'user_id']]
    postable.purchase_time = pd.to_datetime(postable.purchase_time,format = '%H%M%S')
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


def getallpos(pos=None,update=False):
    if from_sql == True:
        pos1 = getposdb(posdb=pos,update=update)
    else:
        pos1 = postable('unified').table
        latest_date = max(pos1.purchase_date)
        pos2 = postable2()
        pos2 = pos2[pos2.purchase_date>latest_date]
        pos1 = pos1.append(pos2)
    pos1.cost = pos1.cost.fillna(0)
#    pos1.price = pos1.price.fillna(0)
#    pos1.cost = pos1.cost.astype('int')
#    pos1.price = pos1.price.astype('int')
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
    if from_sql == True:
        user = getuserdb()
        user.loc[:,'user_id'] = [x[0:12] for x in user.loc[:,'user_id']]
        user.user_rank = user.user_rank.replace(gradedic)
        user = user.set_index('user_id')

        return(user)
    getuserdb,getposdb
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
