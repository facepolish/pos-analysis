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


posfile = 'pos.csv'
userfile = 'user.csv'
#filepos = '../../../output/'
#fileinputpos = '../../../input/'
filepos = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/output/'
fileinputpos = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/input/'
ext = '.csv'
col_dtype_new = {'user_id':str,'user_rank':str}
col_dtype = {u'会員番号':str,u'会員カード番号':str,'user_id':str,'user_rank':str,u'商品コード':str,u'カテゴリコード':str,u'カテゴリーコード':str,u'ショップコード':str, u'商品分類1コード':str,u'商品分類2コード':str,u'商品分類3コード':str,'user_id':str,'user_rank':str} 

colnamedic = {u'店舗ｺｰﾄﾞ':'shop',
              u'店名':'shop_name',
              u'売上日付':'purchase_date',
              u'注文日':'purchase_date',
              u'受注日':'purchase_date',# genesis order table
              u'受注番号':'order_code', # genesis order table & AcceptDetail. key for Merge
              u'売上時間':'purchase_time',
#              u'会員番号':'user_id',
              u'会員カード番号':'user_id',
              u'生年月日':'birth_date',
              u'顧客コード':'user_code', # genesis customer table & order table
              u'ブランド':'brand',
              u'型名':'type',
              u'商品名':'item_name',
              u'金額(税込)':'price', # genesis order table
#              u'商品金額合計':'price',
              u'注文金額合計':'price',  #ECbeing sales
              u'売価':'price', # pos table
              u'数量':'amount',
              u'都道府県':'address',
              u'性別':'gender',
              u'年齢':'age',
              u'年代':'age_group',
              u'来店回数':'visit_count',
              u'仮登録日':'registered_date',
              u'会員ランク':'user_rank',
              u'分類名':'category',
              u'商品コード':'itemcode',
              u'品番名':'item_code1',
              u'ショップコード':'shop_code',
              u'カテゴリーコード':'categorycode',
              u'カテゴリコード':'categorycode',
              u'【ecbeing】カテゴリコード':'categorycode',
              u'【genesis】商品分類1+2+3':'genesis',
              'S_DEPT':'SDEPT',
              u'商品分類1コード':'itemcode1',
              u'商品分類2コード':'itemcode2',
              u'商品分類3コード':'itemcode3',
              u'売上額':'price',
              u'POS販売時刻':'purchase_time',
              u'売上伝票番号':'slip_id'}


posnamelist = ['pos_2011','pos_2012','pos_2013','pos_2014','pos_2015','pos_2016','pos_2017']

@jit
def count_days (days):
    sorted_days = sorted(days)
    counter = 1
    day = sorted_days[0].date()
    for d in sorted_days:
        today = d.date()
        if day != today:
            counter+=1
            day = today
    return(counter)

def StandardVec(table):
    dlist = table.columns
    index0 = [0]
    sumvec = pd.DataFrame(0,index = index0,columns = dlist)
    for dep in dlist:
        l = table.loc[:,dep]
        sumvec.loc[0,dep] = sum(l)
    total = sum(sumvec.loc[0])
    return(sumvec, float(total))
    
def CreateHeatTable(table,svec):
    dlist = table.columns
    indexlist = table.index
    heattable = pd.DataFrame(0,index = indexlist,columns = dlist)
    for row in indexlist:
        total = float(sum(table.loc[row]))
        heattable.loc[row] = table.loc[row]/total
        for col in dlist:
            if svec.loc[0,col] == 0:
                heattable.loc[row,col]=0
            else:
                heattable.loc[row,col]=heattable.loc[row,col]/svec.loc[0,col]
    return(heattable)

def simpleheattable(table):
    vec,total = StandardVec(table)
    vec = vec/total
    ht = CreateHeatTable(table,vec)
    return(ht)
    
def heatTable(table1,table2):
    mvec,msum = StandardVec(table1)
    fvec,fsum = StandardVec(table2)
    totalvec = mvec+fvec
    total = msum+fsum
    totalvec = totalvec/total
    mt = CreateHeatTable(table1,totalvec)
    ft = CreateHeatTable(table2,totalvec)
    return(mt,ft)

class Aggregate(object):
    def __init__(self,ind,colm,coldic,filename):
        self.table = pd.DataFrame(0,index = ind,columns = colm)
        self.coldic = coldic
        if os.path.exists(filename):
            self.prfile= True
        else:
            self.prfile= False
    def __enter__(self):
        return(self)
    def __exit__(self, exc_type, exc_value, traceback):
        self.table.rename(columns = self.coldic,inplace = True)
        self.table.to_csv(filename)

    def AddValue(self,x,y,val):
        self.table.loc[x,y]+=val

def Item3(datatable,year,depttable,shopn,prefix = 'DF_'):
    fileprefix = filepos+prefix
    ysext = str(year)+ext
    target_file = fileprefix+'SalesByDays'+ysext
    if os.path.exists(target_file):
        return

    DEPTlist = depttable.uniqdept
#    shoplist = pd.Series.unique(datatable.shop)
    if prefix == 'web':
        webflag = 1
        shoplist = ['web']
    else:
        webflag = 0
        shoplist = shopn.shopname_table.index
    
    indexlist = [x for x in range(130)]
    monthlist = [x for x in range(13)]
#    if webflag == 0:
#        brandlist = pd.Series.unique(datatable.brand)
    min_date = min(datatable.purchase_date)
    max_date = max(datatable.purchase_date)
    day_count = (max_date-min_date).days
    day_serial = [i for i in range(day_count+1)]
    day_dic = {i:(min_date+datetime.timedelta(days = i)) for i in range(day_count+1) }
    with Aggregate(['Sales'],day_serial,fileprefix+'SalesByDays'+ysext,col_dic = day_dic) as ds, \
        Aggregate(monthlist,DEPTlist,fileprefix+'ItemByyMonth'+ysext,col_dic = depttable.namedic) as mt, \
        Aggregate(monthlist,shoplist,fileprefix+'MonthShop'+ysext,col_dic = shopn.namedic) as ms, \
        Aggregate(shoplist,DEPTlist,fileprefix+'ShopItem'+ysext,in_dic = shopn.namedic,col_dic = depttable.namedic) as si, \
        Aggregate(shoplist,DEPTlist,fileprefix+'ShopItemCount'+ysext,in_dic = shopn.namedic,col_dic = depttable.namedic) as sic:

        maxi = datatable.shape[0]
        print(datatable.shape)
        cc =0
        print ("item module loop count is "+str(maxi))
        
        for index, thisrow in datatable.iterrows():
            if cc%10000 == 0:
                print('progressing counter = '+str(cc))
                r = 100*float(cc)/maxi
                print ("Now "+str(r)+" %")
                cc+=1
            else:
                cc+=1
            item = thisrow.DEPT
            month = thisrow.purchase_date.month
            price = thisrow.price
            if webflag == 0:
                shop = thisrow.shop
            else:
                shop = 'web'
            mt.AddValue(month,item,price)
            ms.AddValue(month,shop,price)
            si.AddValue(shop,item,price)
            sic.AddValue(shop,item,1)
            day_diff = thisrow.purchase_date - min_date
            ds.AddValue('Sales',int(day_diff.days),price)
        
    HMonthTable=simpleheattable(mt.table)
    HMonthTable.rename(columns = depttable.namedic,inplace = True)
    HMonthTable.to_csv(fileprefix+'HItemByyMonth'+ysext)

    HShopItem=simpleheattable(si.table)
    HShopItem.rename(columns = depttable.namedic,index = shopn.namedic,inplace = True)
    HShopItem.to_csv(fileprefix+'HShopItem'+ysext)

#@jit
def Item(datatable,year,usertable,depttable,shopn,prefix = 'pos'):
    fileprefix = filepos+prefix
    ysext = str(year)+ext
    target_file = fileprefix+'ItemByyAgeM'+ysext
    if os.path.exists(target_file):
        return
    datatable = datatable[datatable.user_id.isin(usertable.index)]
     
#    print('start sorting')
#    datatable = datatable.sort_values(by=['DEPT','SDEPT'])
#    print('end sorting')
    # Create Item x Age x Gender table
#    datatable = data.table
#    DEPTlist = pd.Series.unique(datatable.DEPT)
    DEPTlist = depttable.uniqdept
#    shoplist = pd.Series.unique(datatable.shop)
    if prefix == 'web':
        webflag = 1
        shoplist = ['web']
    else:
        webflag = 0
        shoplist = shopn.shopname_table.index
    
    indexlist = [x for x in range(130)]
    monthlist = [x for x in range(13)]
    if webflag == 0:
        brandlist = pd.Series.unique(datatable.brand)
    min_date = min(datatable.purchase_date)
    max_date = max(datatable.purchase_date)
    day_count = (max_date-min_date).days
    day_serial = [i for i in range(day_count+1)]
    day_dic = {i:(min_date+datetime.timedelta(days = i)) for i in range(day_count+1) }

    daily_sales = pd.DataFrame(0,index = ['Sales'],columns = day_serial)

    maleTable = pd.DataFrame(0,index = indexlist,columns=DEPTlist)
    femaleTable = pd.DataFrame(0,index = indexlist,columns=DEPTlist)
    MonthTable = pd.DataFrame(0,columns = DEPTlist,index = monthlist )
    itemtables = [maleTable,femaleTable,MonthTable]

    MonthShop =  pd.DataFrame(0,columns = shoplist,index = monthlist )
    ShopAgeM = pd.DataFrame(0,index = indexlist,columns=shoplist)
    ShopAgeF = pd.DataFrame(0,index = indexlist,columns=shoplist)

    if webflag == 0:
        ShopBrand = pd.DataFrame(0,index = brandlist,columns=shoplist)
        BrandAgeM = pd.DataFrame(0,index = indexlist,columns=brandlist)
        BrandAgeF = pd.DataFrame(0,index = indexlist,columns=brandlist)

    ShopTables = [ShopAgeM,ShopAgeF,MonthShop]

    ShopItem = pd.DataFrame(0,columns = DEPTlist,index = shoplist)
    ShopItemCount = pd.DataFrame(0,columns = DEPTlist,index = shoplist)


    maxi = datatable.shape[0]
    print(datatable.shape)
    cc =0
    print ("item module loop count is "+str(maxi))
    
    for index, thisrow in datatable.iterrows():

        if cc%10000 == 0:
            print('progressing counter = '+str(cc))
            r = 100*float(cc)/maxi
            print ("Now "+str(r)+" %")
            cc+=1
        else:
            cc+=1

        
        item = thisrow.DEPT
        user = thisrow.user_id
        gender = usertable.loc[user,'gender']
        age = usertable.loc[user,'age']
        month = thisrow.purchase_date.month
        price = thisrow.price
        if webflag == 0:
            brand = thisrow.brand
            shop = thisrow.shop
            ShopBrand.loc[brand,shop] = ShopBrand.loc[brand,shop]+price
        else:
            shop = 'web'

        MonthTable.loc[month,item] = MonthTable.loc[month,item]+price
        ShopItem.loc[shop,item] = ShopItem.loc[shop,item]+price
        ShopItemCount.loc[shop,item] = ShopItemCount.loc[shop,item]+1
        MonthShop.loc[month,shop] = MonthShop.loc[month,shop]+price
        day_diff = thisrow.purchase_date - min_date
        daily_sales.loc['Sales',int(day_diff.days)] += price
        
        if age > 0:
            if gender == u'男性':
                maleTable.loc[int(age),item]=maleTable.loc[int(age),item]+price
                ShopAgeM.loc[int(age),shop]=ShopAgeM.loc[int(age),shop]+price
                if webflag == 0:
                    BrandAgeM.loc[int(age),brand]=BrandAgeM.loc[int(age),brand]+price
                
            else:
                femaleTable.loc[int(age),item]=femaleTable.loc[int(age),item]+price
                ShopAgeF.loc[int(age),shop]=ShopAgeF.loc[int(age),shop]+price
                if webflag == 0:
                    BrandAgeF.loc[int(age),brand]=BrandAgeF.loc[int(age),brand]+price
    
    
    HmaleTable,HfemaleTable = heatTable(maleTable,femaleTable)
    
    maleTable.rename(columns = depttable.namedic,inplace = True)
    HmaleTable.rename(columns = depttable.namedic,inplace = True)
    
    femaleTable.rename(columns = depttable.namedic,inplace = True)
    HfemaleTable.rename(columns = depttable.namedic,inplace = True)
    
    HMonthTable=simpleheattable(MonthTable)
    MonthTable.rename(columns = depttable.namedic,inplace = True)
    HMonthTable.rename(columns = depttable.namedic,inplace = True)
    
    daily_sales.rename(columns = day_dic,inplace = True)
    

    maleTable.to_csv(target_file)
    HmaleTable.to_csv(fileprefix+'HItemByyAgeM'+ysext)
    femaleTable.to_csv(fileprefix+'ItemByyAgeF'+ysext)
    HfemaleTable.to_csv(fileprefix+'HItemByyAgeF'+ysext)
    MonthTable.to_csv(fileprefix+'ItemByyMonth'+ysext)
    HMonthTable.to_csv(fileprefix+'HItemByyMonth'+ysext)
    
    daily_sales.to_csv(fileprefix+'SalesByDays'+ysext)

    HShopItem=simpleheattable(ShopItem)
    ShopItem.rename(columns = depttable.namedic,index = shopn.namedic,inplace = True)
    ShopItemCount.rename(columns = depttable.namedic,index = shopn.namedic,inplace = True)
    HShopItem.rename(columns = depttable.namedic,index = shopn.namedic,inplace = True)
    
    HShopAgeM,HShopAgeF = heatTable(ShopAgeM,ShopAgeF)
    ShopAgeM.rename(columns = shopn.namedic,inplace = True)
    HShopAgeM.rename(columns = shopn.namedic,inplace = True)

    ShopAgeF.rename(columns = shopn.namedic,inplace = True)
    HShopAgeF.rename(columns = shopn.namedic,inplace = True)
    
    MonthShop.rename(columns = shopn.namedic,inplace = True)

    ShopItem.to_csv(fileprefix+'ShopItem'+ysext)
    ShopItemCount.to_csv(fileprefix+'ShopItemCount'+ysext)
    HShopItem.to_csv(fileprefix+'HShopItem'+ysext)
    

    ShopAgeM.to_csv(fileprefix+'ShopAgeM'+ysext)
    HShopAgeM.to_csv(fileprefix+'HShopAgeM'+ysext)
    ShopAgeF.to_csv(fileprefix+'ShopAgeF'+ysext)
    HShopAgeF.to_csv(fileprefix+'HShopAgeF'+ysext)
    MonthShop.to_csv(fileprefix+'MonthShop'+ysext)

    if webflag == 0:
        ShopBrand.rename(columns = shopn.namedic,inplace = True)
        ShopBrand.to_csv(fileprefix+'ShopBrand'+ysext)
        BrandAgeM.to_csv(fileprefix+'BrandAgeM'+ysext)
        BrandAgeF.to_csv(fileprefix+'BrandAgeF'+ysext)
    

    return(itemtables,ShopTables,ShopItem)

def high_all_ratio (table,base_col,target_col,prefix = ''):
    basesum = table.loc[:,base_col].sum()
    base_ratio = prefix+'base_ratio'
    target_ratio = prefix+'target_ratio'
    base_target = prefix+'target/base'
    table.loc[:,base_ratio] = table.loc[:,base_col] / (float(basesum))
    targetsum = table.loc[:,target_col].sum()
    table.loc[:,target_ratio] = table.loc[:,target_col] / (float(targetsum))
    table.loc[:,base_target] = table.loc[:,target_ratio] / table.loc[:,base_ratio]
    table = table.sort_values(by=[base_target], ascending=False)
    return(table)

        
class shopname(object):
    def __init__(self,filename):
        self.shopname_table = pd.read_csv(fileinputpos+filename+ext,encoding = 'CP932',index_col=0)
        self.shopname_table.rename(columns=colnamedic, inplace=True)

        self.namedic = {}
        for shopid in self.shopname_table.index:
            self.namedic[shopid] = self.shopname_table.loc[shopid].shop_name

class DEPTtable (object):
    def __init__(self,filename):
        self.depttable = pd.read_csv(fileinputpos+filename+ext,encoding = 'CP932')
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
            
#@jit
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
        if cc%10000 == 0:
            print('progressing counter = '+str(cc))
            r = 100*float(cc)/maxcount
            print ("Now "+str(r)+" %")
        cc += 1

#    plt.bar(x_axix,SalesByAge)
#    plt.show()


    return(SalesByAge,CountByAge)

#@jit
def UserByAge(usertable,prefix=''):
    maiefile = filepos+prefix+'maleage'+ext
    femaiefile = filepos+prefix+'femaleage'+ext
    if os.path.exists(maiefile) and os.path.exists(maiefile):
        return

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
    malebyage.to_csv(maiefile)
    femalebyage.to_csv(femaiefile)
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
        datatable.user_id = datatable.user_id.astype(str)
        datatable.purchase_date = pd.to_datetime(datatable.purchase_date,format = '%Y/%m/%d')
        self.table = datatable

class postable(itemsalestable):
    def __init__(self,filename):
        super(postable,self).__init__(filename)
        self.prefix = 'pos'

class birthtable(object):
    def __init__(self):
        filepath = fileinputpos+u'180823会員_性別・年齢.xlsx'
        convertedfile = fileinputpos+'cleanubirth'+ext
        if os.path.exists(convertedfile):
            df = pd.read_csv(convertedfile,encoding = 'CP932',dtype = col_dtype)
            df.birth_date = pd.to_datetime(df.birth_date,format='%Y/%m/%d')
        else:
            
            df = pd.read_excel(filepath,encoding = 'CP932',dtype = col_dtype)
            df.rename(columns=colnamedic, inplace=True)
            df.user_id = df.user_id.str[0:12]
            df.birth_date = pd.to_datetime(df.birth_date,format='%Y/%m/%d')
            df.user_id.head(15)
            df.to_csv(fileinputpos+'cleanubirth'+ext)
        self.table = df

class gentype (object):
    def __init__(self,tup):
        self.gen1 = tup[0]
        self.gen2 = tup[1]
        self.gen3 = tup[2]
        
class DEPTSDEPT(object):
    def __init__(self,tup):
        self.DEPT = tup[0]
        self.SDEPT = tup[1]
'''
class webtable(itemsalestable):
    gentoecfile = 'gentoec'
    folder3 = 'webshop/'    
    _cnvtable = pd.read_csv(fileinputpos+'webshop/dept_ganesis'+ext,encoding = 'CP932',dtype = col_dtype)
    _cnvtable.rename(columns = colnamedic,inplace = True)
    _code1list = pd.Series.unique(_cnvtable.itemcode1)
    _code2list = pd.Series.unique(_cnvtable.itemcode2)
    _code3list = pd.Series.unique(_cnvtable.itemcode3)
    cvpanel = pd.Panel(0,items = _code1list, major_axis = _code2list,minor_axis = _code3list)
    for i,_row in _cnvtable.iterrows():
        dt = DEPTSDEPT((_row.DEPT,_row.SDEPT))
        cvpanel.loc[_row.itemcode1,_row.itemcode2,_row.itemcode3] = dt

    gentoectable = pd.read_csv(fileinputpos+folder3+gentoecfile+ext,encoding = 'CP932',dtype = col_dtype)
    gentoectable.rename(columns = colnamedic,inplace = True)
    eccodelist = pd.Series.unique(gentoectable.categorycode)
    ectogencode = pd.DataFrame(0,index = ['gencode'],columns = eccodelist)

    for i, row in gentoectable.iterrows():
        gencode = row.genesis
        print ('this row is '+row.genesis+'   '+row.categorycode)
        gen1 = gencode[0:2]
        gen2 = gencode[2:7]
        if gen2 == '99999':
            gen2 = '999999'
            gen3 = gencode[8:]
        else:
            gen3 = gencode[7:]
#        gen1 = int(gen1)
#        gen2 = int (gen2)
#        if gen3.isdigit():
#            gen3 = int(gen3)
#        else:
#            continue
        
        if (gen1 in cvpanel.items) and (gen2 in cvpanel.major_axis) and (gen3 in cvpanel.minor_axis):
            if not (0 == cvpanel[gen1,gen2,gen3]):
                tu = gentype((gen1,gen2,gen3))
                ectogencode.loc['gencode',row.categorycode] = tu

    def __init__(self,filename):
        super(webtable,self).__init__(filename)
        
class ecbeingtable(webtable):
    folder = 'webshop/ecbeing/order/'
    folder2 = 'webshop/ecbeing/item/'
        
    goodsfile = 'goods'

    itemtoectable = pd.read_csv(fileinputpos+folder2+goodsfile+ext,encoding = 'CP932',dtype = col_dtype)
    itemtoectable.rename(columns = colnamedic,inplace = True)
#    print (' goods table columns')
#    print(itemtoectable.columns)
#    print(itemtoectable.head(10))
    for i in range(len(itemtoectable.categorycode)):
        s = itemtoectable.categorycode[i]
        slis = s.split('-')
        if len(slis)>1:
#            print ('splitted string is '+s)
            itemtoectable.categorycode[i] = slis[1]
    itemcodelist = pd.Series.unique(itemtoectable.categorycode)
    itemtoeccode = pd.DataFrame(0,index = ['eccode'],columns = itemcodelist)
    for i, row in itemtoectable.iterrows():
#        if i%1000 == 0:
#            print ('i = '+str(i))
        itemtoeccode.loc['eccode',row.itemcode] = row.categorycode



    def __init__(self,filename):
        cachefilename = 'cache'+filename
        if not os.path.exists(fileinputpos+self.folder+cachefilename+ext):

            super(ecbeingtable,self).__init__(self.folder+filename)
            datatable2 = pd.read_csv(fileinputpos+self.folder2+self.goodsfile+ext,encoding = 'CP932',dtype = col_dtype)
            datatable2.rename(columns = colnamedic, inplace = True)
            print ('datatable2 goods file columns ')
            print (datatable2.columns)
            self.table = pd.merge(self.table,datatable2,on ='itemcode',how = 'left')
            print ('merged table columns')
            print (self.table.columns)
            print('max rows = ' + str(self.table.shape[0]))
            ChkFlag = 0
            erritems = []
            errcodes = []

            for index,row in self.table.iterrows():
#                print ('index = '+str(index))
                icode = row.itemcode
                if not (icode in self.itemtoeccode.columns):
                    if not(icode in erritems):
                        erritems.append(icode)
                        print ('item code = '+str(icode)+' is missing in goods table')
                        print (row)
                    self.table.drop(index,inplace = True)
                    ChkFlag = 1
                    continue
                eccode = self.itemtoeccode.loc['eccode',icode]
                self.table.loc[index,'eccode'] = eccode
                if not (eccode in self.ectogencode.columns):
                    if not(eccode in errcodes):
                        errcodes.append(eccode)
                        print ('eccode code = '+str(eccode)+' is missing in ectogencode.columns')
                        print (row)
#                    self.table.drop(index,inplace = True)
                    ChkFlag = 1
                    continue                    
                gens = self.ectogencode.loc['gencode',eccode]
                if gens == 0 :
                    if not(eccode in errcodes):
                        errcodes.append(eccode)
                        print ('eccode code = '+str(eccode)+' is missing in ectogencode.columns')
                        print (row)
#                    self.table.drop(index,inplace = True)
                    ChkFlag = 1
                    continue
                gen1 = gens.gen1
                gen2 = gens.gen2
                gen3 = gens.gen3
                
                dep = self.cvpanel.loc[gen1,gen2,gen3]
                self.table.loc[index,'DEPT'] = dep.DEPT
                self.table.loc[index,'SDEPT'] = dep.SDEPT
            print (" missing items are "+str(erritems))
            print (" missing codes are "+str(errcodes))

            if ChkFlag == 0:
                self.table.to_csv (fileinputpos+self.folder+cachefilename+ext)

        else:
            self.table = pd.read_csv(fileinputpos+self.folder+cachefilename+ext,encoding = 'CP932',dtype = col_dtype)
        self.table = self.table.dropna(axis = 0,subset = ['user_id'])
        
        self.prefix = 'web'
        
class genesistable(webtable):
    usercodetable = pd.read_csv(fileinputpos+'webshop/genesis/customer/customer'+ext,encoding = 'CP932',dtype = col_dtype)
    usercodetable.rename(columns = colnamedic,inplace = True)
#    print(usercodetable.head(3))
    
    itemcodetable = pd.read_csv(fileinputpos+'webshop/genesis/item/mitem'+ext,encoding = 'CP932',dtype = col_dtype)
    itemcodetable.rename(columns = colnamedic,inplace = True)
#    print(itemcodetable.head(3))
    
    def __init__(self,filename):
        detailfile = 'AcceptDetail'
        folder = 'webshop/genesis/order/'
        filename = str(filename)
        folder = folder+filename+'/'
        folder = fileinputpos+folder
        cachefilename = 'cache'+filename
        
        if True : #not os.path.exists(folder+cachefilename+ext):
            datatable = pd.read_csv(folder+filename+ext,encoding = 'CP932',dtype = col_dtype)
            datatable.rename(columns = colnamedic,inplace = True)
            print(datatable.head(10))
            datatable.purchase_date = pd.to_datetime(datatable.purchase_date,format = '%Y%m%d')
            self.table = datatable
            self.table.rename(columns = colnamedic,inplace = True)
            self.table = pd.merge(self.table,self.usercodetable, on = 'user_code',how = 'left')
            self.table.user_id = self.table.user_id.str[0:12]
            datatable2 = pd.read_csv(folder+detailfile+ext,encoding = 'CP932',dtype = col_dtype)
            datatable2.rename(columns = colnamedic,inplace = True)
            self.table = pd.merge(self.table, datatable2,on = 'order_code',how = 'left')
            self.table = pd.merge(self.table,self.itemcodetable,on = 'itemcode',how = 'left')

            for i in range(self.table.shape[0]):
                code1 = self.table.loc[self.table.index[i],'itemcode1']
                code2 = self.table.loc[self.table.index[i],'itemcode2']
                code3 = self.table.loc[self.table.index[i],'itemcode3']
                if  (code1==code1 and code2 == code2 and code3 == code3):
                    depts = self.cvpanel.loc[code1,code2,code3]
                    self.table.loc[self.table.index[i], 'DEPT']  = depts.DEPT
                    self.table.loc[self.table.index[i], 'SDEPT'] = depts.SDEPT
            self.table.to_csv(folder+cachefilename+ext)
        else:
            self.table = pd.read_csv(folder+cachefilename+ext,encoding = 'CP932',dtype = col_dtype)


        self.prefix = 'web'


class websalestable(object):
    ren_dic = {u'会員番号':'user_id'}# local hack for genesis customer table
    customertable = pd.read_csv(fileinputpos + 'webshop/genesis/customer/customer.csv',encoding = 'CP932',dtype = col_dtype)
    customertable.rename(columns= colnamedic,inplace=True)
    customertable.rename(columns= ren_dic,inplace=True)
    rem_cols = ['user_id','purchase_date','price']
    def _fixgen(self,gentable):
        gentable = gentable.rename(columns=colnamedic)
#        for i,row in gentable.iterrows():
#            if row.shop_code == '17289':
#                print ("Yes Takasu clinic")
        print ("gentable hight = "+str(gentable.shape[0]))
        gentable = gentable[gentable['shop_code'] == '17289']
        print ("gentable hight = "+str(gentable.shape[0]))
        gentable.purchase_date = pd.to_datetime(gentable.purchase_date,format = '%Y%m%d')
        gentable = pd.merge(gentable,self.customertable,on='user_code',how = 'left')
        gentable = gentable.drop('user_code',axis = 1)
        gentable = gentable.dropna(subset = ['user_id'])
        gentable = gentable.loc[:,self.rem_cols]
        return(gentable)
    def _fixecbeing(self,ectable):
        ectable = ectable.rename(columns=colnamedic)
        ectable = ectable.dropna(subset=['order_code'],axis = 0)
        ectable = ectable.dropna(subset = ['user_id'])
        ectable.purchase_date = pd.to_datetime(ectable.purchase_date,format = '%Y/%m/%d')
        ectable = ectable.loc[:,self.rem_cols]
        return(ectable)
    def __init__(self,year):
        genpath = 'webshop/genesis/order/'
        ecpath = 'webshop/ecbeing/order/'
        if year == 2015:
            gen_15a_file = '2015/2015a.csv'
            gen_15b_file = '2015/2015b.csv'
            filepath = fileinputpos+genpath
            gen_15a = pd.read_csv(filepath+gen_15a_file,encoding = 'CP932')
            gen_15b = pd.read_csv(filepath+gen_15b_file,encoding = 'CP932')
            gen_15a = self._fixgen(gen_15a)
            gen_15b = self._fixgen(gen_15b)
            self.table = gen_15b.append(gen_15a)
        elif year == 2016:
            gen_16_file = '2016/2016.csv'
            ec_16_file = 'sales201601-12.csv'
            filepath = fileinputpos+genpath
            gen_16 = pd.read_csv(filepath+gen_16_file,encoding = 'CP932')
            gen_16 = self._fixgen(gen_16)
            filepath = fileinputpos+ecpath
            ec_16 = pd.read_csv(filepath+ec_16_file,encoding = 'CP932',dtype = col_dtype)
            ec_16 = self._fixecbeing(ec_16)
            self.table = gen_16.append(ec_16)
        elif year == 2017:
            ec_17_file = 'sales201701-12detail'
#            ec_17_file = 'sales201701-12.csv'
#            filepath = fileinputpos+ecpath
#            ec_17 = pd.read_csv(filepath+ec_17_file,encoding = 'CP932',dtype = col_dtype)
#            ec_17 = self._fixecbeing(ec_17)
#            self.table = ec_17
            ect = ecbeingtable(ec_17_file)
            self.table = ect.table
            
'''

