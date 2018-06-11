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

posfile = 'pos.csv'
userfile = 'user.csv'
filepos = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/output/'
fileinputpos = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/input/'
ext = '.csv'
col_dtype_new = {'user_id':str,'rank':str}
col_dtype = {u'会員番号':str,u'会員カード番号':str,'user_id':str,'rank':str,u'商品コード':str,u'カテゴリコード':str,u'カテゴリーコード':str} 

colnamedic = {u'店舗ｺｰﾄﾞ':'shop',
              u'店名':'shop_name',
              u'売上日付':'purchase_date',
              u'注文日':'purchase_date',
              u'受注日':'purchase_date',# genesis order table
              u'受注番号':'order_code', # genesis order table & AcceptDetail. key for Merge
              u'売上時間':'purchase_time',
#              u'会員番号':'user_id',
              u'会員カード番号':'user_id',
              u'顧客コード':'user_code', # genesis customer table & order table
              u'ブランド':'brand',
              u'型名':'type',
              u'商品名':'item_name',
              u'金額(税込)':'price', # genesis order table
              u'商品金額合計':'price',
              u'売価':'price', # pos table
              u'数量':'amount',
              u'都道府県':'address',
              u'性別':'gender',
              u'年齢':'age',
              u'年代':'age_group',
              u'来店回数':'visit_count',
              u'仮登録日':'registered_date',
              u'会員ランク':'rank',
              u'分類名':'category',
              u'商品コード':'itemcode',
              u'品番名':'item_code1',
              u'カテゴリーコード':'categorycode',
              u'カテゴリコード':'categorycode',
              u'【ecbeing】カテゴリコード':'categorycode',
              u'【genesis】商品分類1+2+3':'genesis',
              'S_DEPT':'SDEPT',
              u'商品分類1コード':'itemcode1',
              u'商品分類2コード':'itemcode2',
              u'商品分類3コード':'itemcode3'}


posnamelist = ['pos_2011','pos_2012','pos_2013','pos_2014','pos_2015','pos_2016','pos_2017']


class UserTable(object):
    def __init__(self,filename):
        self.usertable = pd.read_csv(fileinputpos+filename+ext,encoding = 'CP932',dtype = col_dtype_new)
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
            
    
def GetSalesByAge(datatable,usertable,genflag = 'all'):
    x_axix = [x for x in range(130)]

    targetusers = set(usertable.index) & set(datatable.user_id)
    if not (genflag == 'all'):
        if genflag == 'Male':
            ut = usertable[usertable.gender == u'男性']
            limlist = ut.index
        elif genflag == 'Female':
            ut = usertable[usertable.gender == u'女性']
            limlist = ut.index
        targetusers = targetusers & set (limlist)
    print ("condition extraction starts")

    targettable = datatable[datatable.user_id.isin(targetusers)]
    print ("condition extraction end")

    print('start sorting')
    targettable = targettable.sort_values(by=['user_id','purchase_date'])
    print('end sorting')

    SalesByAge = numpy.zeros(130)
    CountByAge = numpy.zeros(130)
    user = 0
    cc = 0
    maxcount = targettable.shape[0]
    for index, thisrow in targettable.iterrows():
        if not user == thisrow.user_id:
            user = thisrow.user_id
            userage = int(usertable.loc[user,'age'])
            CountByAge[userage] += 1
        if userage > 0:
            SalesByAge[userage] += thisrow.price
        if cc%1000 == 0:
            print('progressing counter = '+str(cc))
            r = 100*float(cc)/maxcount
            print ("Now "+str(r)+" %")
        cc += 1

    plt.bar(x_axix,SalesByAge)
    plt.show()


    return(SalesByAge,CountByAge)

def UserByAge(usertable,prefix=''):
    print ('Creating Age by user table')
    x_axix = [x for x in range(130)]
    malebyage = pd.DataFrame(0,index = x_axix,columns =['age'])
    femalebyage = pd.DataFrame(0,index = x_axix,columns =['age'])


    male_count  = 0
    female_count = 0
    for index,row in usertable.iterrows():
        gender = row.gender
        age = row.age
        if age< 0 :
            print ('abnormal negative age has been found')
            age = 0
        if gender == u'男性':
            malebyage.loc[int(age)]+= 1
            male_count +=1
        else:
            femalebyage.loc[int(age)] += 1
            female_count += 1
    malebyage.to_csv(filepos+prefix+'maleage'+ext)
    femalebyage.to_csv(filepos+prefix+'femaleage'+ext)
    print("male = "+str(male_count))
    print("female = "+str(female_count))
    ra = float(male_count)/float(male_count+female_count)
    print ("male / female ratio = "+str(ra))
    print ('Age by user table creation end')
    plt.bar(x_axix,malebyage.age)
    plt.show()
    plt.bar(x_axix,femalebyage.age)
    plt.show()

class itemsalestable(object):
    def __init__(self,filename):
        datatable = pd.read_csv(fileinputpos+filename+ext,encoding = 'CP932',dtype = col_dtype)
        datatable.rename(columns = colnamedic, inplace = True)
        datatable.purchase_date = pd.to_datetime(datatable.purchase_date,format = '%Y/%m/%d')
        self.table = datatable

class postable(itemsalestable):
    def __init__(self,filename):
        super(postable,self).__init__(filename)
        self.prefix = 'pos'
