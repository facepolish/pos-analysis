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

def createHash(userid):
    print(userid)
    return hashlib.md5(userid).hexdigest()

def convertList (InList):
    NewList = []

    for item in InList:
        NewList.append(createHash(item))
        

def IDtoHash(filename):
    infile = '../input/'+filename
    outfile = '../output/'+filename
    
    table = pd.read_csv(infile)
    table['hashedid'] = createHash(table['id'])
    table.drop('id',axix = 1)
    table.to_csv(outfile)

def cleanmembertable():
    filepath = fileinputpos+'HITRMD_KJSMBR'+ext
    df = pd.read_csv(filepath,encoding = 'CP932',dtype = col_dtype)
    df.rename(columns=colnamedic, inplace=True)
    df.user_id = df.user_id.str[0:12]
    df.user_id.head(15)
    df.to_csv(fileinputpos+'cleanutable'+ext)
    
def CleanUpPosTable (Ori,Tofile):
    filepath = fileinputpos + Ori+ ext
    df = pd.read_csv(filepath,encoding = 'CP932',dtype = col_dtype)
    df.rename(columns=colnamedic, inplace=True)
    df.user_id = df.user_id.str[0:12]
    df.purchase_date = pd.to_datetime(df.purchase_date,format = '%Y%m%d')
    df.purchase_date = df.purchase_date.apply(lambda x:x.strftime('%Y/%m/%d'))

    df.to_csv(fileinputpos + Tofile + ext)
    
    return(df)
def CleanFiles ():
    namelist = ['uri_2011','uri_2012','uri_2013','uri_2014','uri_2015','uri_2016','uri_2017']
    for (a,b) in zip(namelist,posnamelist):
        CleanUpPosTable(a,b)


def MergeTable():
    CleanFiles ()

    filepath = fileinputpos+'pos_2011'+ext
    
    df = pd.read_csv(filepath,encoding = 'CP932',dtype = col_dtype_new)

    for filename in posnamelist:
        filepath = fileinputpos+filename+ext
        print(filepath)
        block = pd.read_csv(filepath,encoding= 'CP932',dtype = col_dtype_new)

        df = pd.concat([df,block])
#    for datet in df.purchase_date:
#        print(datet.strftime('%Y/%m/%d'))

    df.to_csv(fileinputpos+'unified'+ext)


def RecurringPurchaseCheck(datatable, targettable,usertable,PositiveCheck = True):
    PurchaseByAge = numpy.zeros(130)
    print ('extracting source unique users ')
    sourcelist = pd.Series.unique(datatable.user_id)
#    print(sourcelist.head(3))
    print ('extracting target unique users ')
    targetlist = pd.Series.unique(targettable.user_id)
    length = len(sourcelist)
#    print(targetlist.head(3))
    for userid in sourcelist:
        length = length -1
        if length% 1000 == 0:
            print ('remaining = '+str(length))
#       print('checking user = '+userid)
 

        if not (PositiveCheck ^ (userid in targetlist)):
            userage = usertable.GetAge(userid)
#            print ('age of this user is '+str(userage))
            PurchaseByAge[int(userage)]=PurchaseByAge[int(userage)]+1
    return(PurchaseByAge)



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
        
class shopname(object):
    def __init__(self,filename):
        self.shopname_table = pd.read_csv(fileinputpos+filename+ext,encoding = 'CP932',index_col=0)
        self.shopname_table.rename(columns=colnamedic, inplace=True)

        self.namedic = {}
        for shopid in self.shopname_table.index:
            self.namedic[shopid] = self.shopname_table.loc[shopid].shop_name
    

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

def ItemByItem(datatable,usertable,depttable):
    datatable = datatable.sort_values(by=['purchase_date','user_id'])
    DEPTlist = pd.Series.unique(datatable.DEPT)
    brandlist = pd.Series.unique(datatable.brand)
    deptbydept = pd.DataFrame(0,columns= DEPTlist,index = DEPTlist)
    brandbybrand = pd.DataFrame(0,columns = brandlist, index = brandlist)
    
    maxi = datatable.shape[0]
    i = 0
    while i<maxi:
        this_day = datatable.purchase_date[i]
        this_user = datatable.user_id[i]
        item_list = [datatable.DEPT[i]]
        brand_list = [datatable.brand[i]]
        if i% 10000 == 0:
            print ('ItemByItem remaining = '+str(maxi-i))
            print ('this day = '+str(this_day))

        i = i+1
        while i<maxi and this_day == datatable.purchase_date[i] and this_user == datatable.user_id[i]:
            if not (datatable.DEPT[i] in item_list):
                item_list.append(datatable.DEPT[i])
            if not (datatable.brand[i] in brand_list):
                brand_list.append(datatable.brand[i])
            i= i+1
        if (len(item_list)>1):
            for (j,item) in enumerate(item_list):
                for item2 in item_list[j:]:
                    deptbydept[item].loc[item2]= deptbydept[item].loc[item2]+1
        if (len(brand_list)>1):
            for (j,item) in enumerate(brand_list):
                for item2 in brand_list[j:]:
                    brandbybrand[item].loc[item2]= brandbybrand[item].loc[item2]+1
                 
    for item in DEPTlist:
        itemcount = deptbydept[item].loc[item]
        deptbydept[item] = deptbydept[item]/(float(itemcount))
    deptbydept.rename(columns = depttable.namedic,index = depttable.namedic,inplace = True)
    deptbydept.to_csv(filepos+'deptbydept'+ext)

    for item in brandlist:
        itemcount = brandbybrand[item].loc[item]
        brandbybrand[item] = brandbybrand[item]/(float(itemcount))
    brandbybrand.rename(columns = depttable.namedic,inplace = True)
    brandbybrand.to_csv(filepos+'brandbybrand'+ext)


        
    
    
def Item(data,year,usertable,depttable,shopn):
     
#    print('start sorting')
#    datatable = datatable.sort_values(by=['DEPT','SDEPT'])
#    print('end sorting')
    # Create Item x Age x Gender table
    datatable = data.table
    ysext = str(year)+ext
#    DEPTlist = pd.Series.unique(datatable.DEPT)
    DEPTlist = depttable.uniqdept
#    shoplist = pd.Series.unique(datatable.shop)
    if data.prefix == 'web':
        webflag = 1
        shoplist = ['web']
    else:
        webflag = 0
        shoplist = shopn.shopname_table.index
    
    indexlist = [x for x in range(130)]
    monthlist = [x for x in range(13)]
    if webflag == 0:
        brandlist = pd.Series.unique(datatable.brand)

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
    
    for index, thisrow in datatable.iterrows():
        
        item = thisrow.DEPT
        user = thisrow.user_id
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
        
        if usertable.CheckRegistration(user):
            row = usertable.currentuser
            if row.age > 0:
                if row.gender == u'男性':
                    maleTable.loc[int(row.age),item]=maleTable.loc[int(row.age),item]+price
                    ShopAgeM.loc[int(row.age),shop]=ShopAgeM.loc[int(row.age),shop]+price
                    if webflag == 0:
                        BrandAgeM.loc[int(row.age),brand]=BrandAgeM.loc[int(row.age),brand]+price
                    
                else:
                    femaleTable.loc[int(row.age),item]=femaleTable.loc[int(row.age),item]+price
                    ShopAgeF.loc[int(row.age),shop]=ShopAgeF.loc[int(row.age),shop]+price
                    if webflag == 0:
                        BrandAgeF.loc[int(row.age),brand]=BrandAgeF.loc[int(row.age),brand]+price
    
    
    HmaleTable,HfemaleTable = heatTable(maleTable,femaleTable)
    
    maleTable.rename(columns = depttable.namedic,inplace = True)
    HmaleTable.rename(columns = depttable.namedic,inplace = True)
    
    femaleTable.rename(columns = depttable.namedic,inplace = True)
    HfemaleTable.rename(columns = depttable.namedic,inplace = True)
    
    HMonthTable=simpleheattable(MonthTable)
    MonthTable.rename(columns = depttable.namedic,inplace = True)
    HMonthTable.rename(columns = depttable.namedic,inplace = True)
    
    fileprefix = filepos+data.prefix

    maleTable.to_csv(fileprefix+'ItemByyAgeM'+ysext)
    HmaleTable.to_csv(fileprefix+'HItemByyAgeM'+ysext)
    femaleTable.to_csv(fileprefix+'ItemByyAgeF'+ysext)
    HfemaleTable.to_csv(fileprefix+'HItemByyAgeF'+ysext)
    MonthTable.to_csv(fileprefix+'ItemByyMonth'+ysext)
    HMonthTable.to_csv(fileprefix+'HItemByyMonth'+ysext)

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

                    

class gentype (object):
    def __init__(self,tup):
        self.gen1 = tup[0]
        self.gen2 = tup[1]
        self.gen3 = tup[2]
        
class DEPTSDEPT(object):
    def __init__(self,tup):
        self.DEPT = tup[0]
        self.SDEPT = tup[1]

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
        gen1 = int(gen1)
        gen2 = int (gen2)
        if gen3.isdigit():
            gen3 = int(gen3)
        else:
            continue
        
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
    print (' goods table columns')
    print(itemtoectable.columns)
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
        if i%1000 == 0:
            print ('i = '+str(i))
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

            for index,row in self.table.iterrows():
#                print ('index = '+str(index))
                icode = row.itemcode
                if not (icode in self.itemtoeccode.columns):
                    print ('item code = '+str(icode)+' is missing in goods table')
                    self.table.drop(index,inplace = True)
                    ChkFlag = 1
                    continue
                eccode = self.itemtoeccode.loc['eccode',icode]
                if not (eccode in self.ectogencode.columns):
                    print ('error in eccode = '+str(eccode))
                    self.table.drop(index,inplace = True)
                    ChkFlag = 1
                    continue                    
                gens = self.ectogencode.loc['gencode',eccode]
                if gens == 0 :
                    print ('error in eccode = '+str(eccode))
                    self.table.drop(index,inplace = True)
                    ChkFlag = 1
                    continue
                gen1 = gens.gen1
                gen2 = gens.gen2
                gen3 = gens.gen3
                
                dep = self.cvpanel.loc[gen1,gen2,gen3]
                self.table.loc[index,'DEPT'] = dep.DEPT
                self.table.loc[index,'SDEPT'] = dep.SDEPT
            if ChkFlag == 0:
                self.table.to_csv (fileinputpos+self.folder+cachefilename+ext)
        else:
            self.table = pd.read_csv(fileinputpos+self.folder+cachefilename+ext,encoding = 'CP932',dtype = col_dtype)
        
        self.prefix = 'web'
        
class genesistable(webtable):
    usercodetable = pd.read_csv(fileinputpos+'webshop/genesis/customer/customer'+ext,encoding = 'CP932',dtype = col_dtype)
    usercodetable.rename(columns = colnamedic,inplace = True)
    print(usercodetable.head(3))
    
    itemcodetable = pd.read_csv(fileinputpos+'webshop/genesis/item/mitem'+ext,encoding = 'CP932',dtype = col_dtype)
    itemcodetable.rename(columns = colnamedic,inplace = True)
    print(itemcodetable.head(3))
    
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


def ShopSalesByYear(shopn,postables):
    ShopSalesByYearTable = pd.DataFrame(0,index = postables.keys(),columns = shopn.namedic.keys())
    for year in postables.keys():
        postable = postables[year].table
        print(postable.head(5))
        thistable = postable.sort_values(by = ['shop','purchase_date'])
        print(thistable.head(5))
        i = 0
        maxi = thistable.shape[0]
        while i<maxi:
            thisshop = thistable.iloc[i].shop
            print ('processing '+shopn.namedic[thisshop]+' for year '+str(year))
            sumprice = thistable.iloc[i].price
            i= i+1
            while i<maxi and thisshop == thistable.iloc[i].shop:
                sumprice = sumprice + thistable.iloc[i].price
                i= i+1
            ShopSalesByYearTable.loc[year,thisshop] = sumprice
    ShopSalesByYearTable.rename(columns = shopn.namedic,inplace = True)
    ShopSalesByYearTable.to_csv(filepos+'ShopSalesByYear'+ext)
    
def ClusterAnalysis(prefix,table,usert,shopn):
    shoplist = shopn.shopname_table.index

    year_list = [2011,2012,2013,2014,2015,2016,2017]
    MonthList = [x for x in range(13)]
    agelist = [x for x in range(130)]
    itemtablecol = ['SDEPT','totalprice','count']

    ShopTable = pd.DataFrame(0,index = year_list,columns = shoplist)
    MonthTable = pd.DataFrame(0,index = year_list, columns = MonthList)
    regyearTable = pd.DataFrame(0,index = year_list,columns = usert.regyearlist)

    MAge = pd.DataFrame(0,index = year_list,columns = agelist)
    FAge = pd.DataFrame(0,index = year_list,columns = agelist)
#    RankTable = pd.DataFrame(0,index = year_list, coluuns = usert.ranklist)
    
    
    for y in year_list:
        yt = table.where(table.purchase_date.dt.year == y).dropna()
        unqtype = pd.Series.unique(yt.type)
        ItemTable = pd.DataFrame(0,index = unqtype,columns = itemtablecol)
        ItemTable['brand']= ''
        ItemTable['item_name']= ''

        OldLadyItem = pd.DataFrame(0,index = unqtype,columns = itemtablecol)
        OldLadyItem['brand']= ''
        OldLadyItem['item_name']= ''

        for key,row in yt.iterrows():
#            print (row)
            if ItemTable.loc[row.type,'totalprice'] == 0:
                ItemTable.loc[row.type,'brand'] = row.brand
                ItemTable.loc[row.type,'item_name'] = row.item_name
                ItemTable.loc[row.type,'SDEPT'] = row.SDEPT
                
            ItemTable.loc[row.type,'totalprice'] = ItemTable.loc[row.type,'totalprice']+row.price
            ItemTable.loc[row.type,'count'] = ItemTable.loc[row.type,'count'] + row.amount

            shop = row.shop
            ShopTable.loc[y,shop] = ShopTable.loc[y,shop]+row.price
            month = row.purchase_date.month
            MonthTable.loc[y,month]= MonthTable.loc[y,month]+row.price
            user = row.user_id
            if usert.CheckRegistration(user):
                udata = usert.currentuser
                if udata.gender == u'男性':
                    MAge.loc[y,udata.age] = MAge.loc[y,udata.age] +row.price
                else:
                    FAge.loc[y,udata.age] = FAge.loc[y,udata.age] +row.price
                    
                    if udata.age>64 and udata.age <72:
                        if OldLadyItem.loc[row.type,'totalprice'] == 0:
                            OldLadyItem.loc[row.type,'brand'] = row.brand
                            OldLadyItem.loc[row.type,'item_name'] = row.item_name
                            OldLadyItem.loc[row.type,'SDEPT'] = row.SDEPT
                        OldLadyItem.loc[row.type,'totalprice'] = ItemTable.loc[row.type,'totalprice']+row.price
                        OldLadyItem.loc[row.type,'count'] = ItemTable.loc[row.type,'count'] + row.amount
                        
                        
#                RankTable.loc[y,udata.rank] = RankTable.loc[y,udata.rank]+1
                regyearTable.loc[y,udata.registered_date.year] = regyearTable.loc[y,udata.registered_date.year] +row.price
        ItemTable.to_csv(filepos+prefix+'CItem'+str(y)+ext)
        OldLadyItem.to_csv(filepos+prefix+'COldL'+str(y)+ext)
        
    
    ShopTable.rename(columns = shopn.namedic,inplace = True)
    ShopTable.to_csv(filepos+prefix+'CShop'+ext)
    MonthTable.to_csv(filepos+prefix+'CMonth'+ext)
    MAge.to_csv(filepos+prefix+'CMAge'+ext)
    FAge.to_csv(filepos+prefix+'CFAge'+ext)
#    RankTable.to_csv(filepos+'CRank'+ext)
    regyearTable.to_csv(filepos+prefix+'Cregyear'+ext)

def MonthlyPrice(prefix,table,y):
    shoplist = shopn.shopname_table.index

    MonthList = [x for x in range(13)]
    itemtablecol = ['totalprice','count','unit_price']

    MonthTable = pd.DataFrame(0,index = MonthList, columns = itemtablecol)

    yt = table.where(table.purchase_date.dt.year == y).dropna()
    for m in MonthList:
        mt = yt.where(yt.purchase_date.dt.month == m).dropna()
        total = sum(mt.price)
        tcount = sum(mt.amount)
        if tcount == 0:
            uprice = 0
        else:
            uprice = total/float(tcount)
        MonthTable.loc[m,'totalprice'] = total
        MonthTable.loc[m,'count'] = tcount
        MonthTable.loc[m,'unit_price'] = uprice
    MonthTable.to_csv(filepos+prefix+'CMonthly'+str(y)+ext)

def UserAnalysis(utable,usert,shopn,depttable):
    highprice = 8000

    """
    print ('User Analysis Start')
    maxvisit = max(usert.usertable.visit_count)
    print ('max visit count is '+str(maxvisit))
    visitc = numpy.zeros([int(maxvisit)+1])
    xlist = [x for x in range(int(maxvisit)+1)]
    for key,row in usert.usertable.iterrows():
        if not math.isnan(row.visit_count):
            v_count = row.visit_count
            if v_count >300:
                print (row)
            visitc[int(row.visit_count)] = visitc[int(row.visit_count)]+1
    plt.bar(xlist,visitc)
    plt.show()
    print ('User Analysis End')
    """
#    table = utable.table.sort_values(by = ['user_id','purchase_date']).dropna()
    table = utable.table.sort_values(by = ['user_id','purchase_date'])
    print ('head = ')
    print (table.head(3))
    print ('tail = ')
    print (table.tail(3))
    idlist = pd.Series.unique(utable.table.user_id)
    itemlist = pd.Series.unique(utable.table.DEPT)
    collist = [2011,2012,2013,2014,2015,2016,2017,'interval','rank']
    YearlySaleByID = pd.DataFrame(0,index = idlist,columns = collist)
    ItemTable1 = pd.DataFrame(0,index = itemlist,columns = itemlist)
    ItemTable2 = pd.DataFrame(0,index = itemlist,columns = itemlist)
    ItemTable3 = pd.DataFrame(0,index = itemlist,columns = itemlist)
    ItemTable4 = pd.DataFrame(0,index = itemlist,columns = itemlist)
    ItemCount = pd.DataFrame(0,index = ['count'],columns = itemlist)
    

    def SetItemTable(todaylist,lastlist,interval):
        tlist = list(set(todaylist))
        
        for (j,x) in enumerate(tlist):
            for y in tlist[j+1:]:
                ItemTable1.loc[x,y] = ItemTable1.loc[x,y]+1
                ItemTable1.loc[y,x] = ItemTable1.loc[x,y]
        for x in lastlist:
            for y in tlist:
                ItemTable2.loc[x,y] = ItemTable2.loc[x,y] + 1
        if interval >30:
            for x in lastlist:
                for y in tlist:
                    ItemTable3.loc[x,y] = ItemTable3.loc[x,y] + 1
        if interval >300:
            for y in tlist:
                ItemCount.loc['count',y] = ItemCount.loc['count',y] + 1
                for x in lastlist:
                    ItemTable4.loc[x,y] = ItemTable4.loc[x,y] + 1

        lastlist = tlist
        tlist = []
        return(tlist,lastlist)


    currentid = 0
    maxrow = table.shape[0]
    print('maxrow = '+str(maxrow))
    i = 0
    while(i<maxrow):
        currentid = table.loc[table.index[i],'user_id']
        if not (currentid == currentid):
            i = i + 1
            continue
        vcount = 1
        daysum = 0
        sdayhighlist = []
        lastdayhighlist = []
        lastvisit =  table.loc[table.index[i],'purchase_date']
        while(i<maxrow and currentid == table.loc[table.index[i],'user_id']):
            thisyear = table.loc[table.index[i],'purchase_date'].year
            ysum = 0
            while (thisyear == table.loc[table.index[i],'purchase_date'].year and currentid == table.loc[table.index[i],'user_id']):
                thisprice = table.loc[table.index[i],'price']
                ysum = ysum + thisprice
                thisdate = table.loc[table.index[i],'purchase_date']
                daysdiff = thisdate - lastvisit
                if (daysdiff.days > 0):
                    vcount = vcount + 1
                    daysum = daysum + daysdiff.days
                    sdayhighlist, lastdayhighlist = SetItemTable( sdayhighlist, lastdayhighlist,daysdiff.days)

                    lastvisit = thisdate
                    
                if (thisprice > highprice):
                    sdayhighlist.append(table.loc[table.index[i],'DEPT']) 
                    
                i = i + 1
                if (i>=maxrow):
                    break
                if i%10000 == 0:
                    print('i = '+str(i))
            YearlySaleByID.loc[currentid,thisyear] = ysum
            sdayhighlist, lastdayhighlist = SetItemTable( sdayhighlist, lastdayhighlist,daysdiff.days)
            
        YearlySaleByID.loc[currentid,'interval'] = daysum/vcount
        if usert.CheckRegistration(currentid):
            YearlySaleByID.loc[currentid,'rank'] = usert.currentuser['rank']
            
    YearlySaleByID = YearlySaleByID.sort_values(by = 2017,ascending=False)
    
    pre = filepos+utable.prefix
    YearlySaleByID.to_csv(pre+'userpurchase'+ext)
    ItemTable1.rename(columns = depttable.namedic,index = depttable.namedic,inplace = True)
    ItemTable1.to_csv(pre+'samedaypurchase'+ext)
    ItemTable2.rename(columns = depttable.namedic,index = depttable.namedic,inplace = True)
    ItemTable2.to_csv(pre+'nextvisitpurchase'+ext)
    ItemTable3.rename(columns = depttable.namedic,index = depttable.namedic,inplace = True)
    ItemTable3.to_csv(pre+'nextMonthpurchase'+ext)

    for g in ItemTable4.index:
        s = sum(ItemTable4.loc[g])
        ItemTable4.loc[g] = 100*(ItemTable4.loc[g]/float(s))
    ItemTable4.rename(columns = depttable.namedic,index = depttable.namedic,inplace = True)
    ItemTable4.to_csv(pre+'nextYearpurchase'+ext)
    
    s = sum(ItemCount.loc['count'])
    ItemCount.loc['count'] = 100*(ItemCount.loc['count']/float(s))
    ItemCount.rename(columns = depttable.namedic,inplace = True)
    ItemCount.to_csv(pre+'nextYearpurchase2'+ext)
    
    

#    datatable = usert.usertable.sort_values(by=['visit_count','purchase_date'])
    
    
def RangeAnalysis(utable,usert,shopn):
    CShoes = 1
    High_Range = [23000,30000]
    Low_Range = [8000,11000]
    table = utable.table
    
    ShoesTable = table.where(table.DEPT == CShoes).dropna()
    table430 = ShoesTable.where(ShoesTable.type == '430').dropna()
    table430HNT = ShoesTable.where(ShoesTable.type == '430_HNT').dropna()
    table430KH = ShoesTable.where(ShoesTable.type == '430_KH').dropna()
    table430 = table430.append(table430HNT)
    table430 = table430.append(table430KH)
    
    MonthlyPrice('i430',table430,2016)
    MonthlyPrice('i430',table430,2017)
    

    
    HighTable = ShoesTable.where(abs(ShoesTable.price) >High_Range[0]).dropna()
    HighTable = HighTable.where(abs(HighTable.price) < High_Range[1]).dropna()
    ClusterAnalysis('High',HighTable,usert,shopn)
    

    LowTable = ShoesTable.where(abs(ShoesTable.price) >Low_Range[0]).dropna()
    LowTable = ShoesTable.where(abs(LowTable.price) < Low_Range[1]).dropna()
    ClusterAnalysis('Low',LowTable,usert,shopn)

    ClusterAnalysis('All',ShoesTable,usert,shopn)
    
    
def SDEPT_analysis(depttable):
    ana_list = [1,14,18]
    year_list = [2011,2012,2013,2014,2015,2016,2017]
    utable = postable('unified')
    tables = {}
    pricemax = 150000
    pricerangelist = [x for x in range(0,pricemax+1000,1000)]
    for item in ana_list:
        tables[item] = utable.table.where(utable.table.DEPT == item).dropna()
        tables[item] = tables[item].sort_values(by = ['SDEPT','type','purchase_date'])
        sdeptlist = pd.Series.unique(tables[item].SDEPT)
        typelist = pd.Series.unique(tables[item].type)
        year_sdept = pd.DataFrame(0,index = year_list,columns = sdeptlist)
        pricerangetable = pd.DataFrame(0,index = year_list,columns = pricerangelist)
        for y in year_list:
            
            yt = tables[item].where(tables[item].purchase_date.dt.year == y).dropna()
            sdlist = pd.Series.unique(yt.SDEPT)
            typelist1 = pd.Series.unique(yt.type)
            typepricetable = pd.DataFrame(0,index = typelist1,columns=['StartPrice','StartD','Total','AveragePrice','StartAverageRatio'])
        
            for sd in sdlist:
                sdtable = yt.where(tables[item].SDEPT == sd).dropna()
                yearsum = sum(sdtable.price)
                year_sdept.loc[y,sd] = yearsum
            
                
                subtypes = pd.Series.unique(sdtable.type)
                for st in subtypes :
                    sttable = sdtable.where(sdtable.type == st).dropna()
                    sttable = sttable.sort_values(by = ['purchase_date'])
                    stp = sttable.loc[sttable.index[0],'price']
                    typepricetable.loc[st,'StartPrice'] = stp
                    typepricetable.loc[st,'StartD'] = sttable.iloc[0].purchase_date
                    pricesum = sum(sttable.price)
                    typepricetable.loc[st,'Total'] = pricesum
                    priceaverage = pricesum/float(len(sttable.price))
                    typepricetable.loc[st,'AveragePrice'] = priceaverage
                    typepricetable.loc[st,'StartAverageRatio'] = float(priceaverage)/float(stp)
                    for i in range(sttable.shape[0]):
                        c = sttable.loc[sttable.index[i],'amount']
                        absstp = abs(sttable.loc[sttable.index[i],'price']/float(c))
                        if absstp>=pricemax:
                            pricerangetable.loc[y,pricemax] = pricerangelist.loc[y,pricemax]+c
                        else:
                            thisrange = 1000*(absstp//1000)
                            pricerangetable.loc[y,thisrange] = pricerangetable.loc[y,thisrange]+c
            print (typepricetable.head(5))
            plt.scatter(typepricetable.Total,typepricetable.StartAverageRatio)
            plt.show()
            typepricetable.to_csv(filepos+depttable.namedic[item]+'type'+str(y)+ext)
            plt.plot(pricerangelist,pricerangetable.loc[y])
            plt.show()
        pricerangetable.to_csv(filepos+depttable.namedic[item]+'range'+ext)
                

        print (year_sdept.head(5))
        year_sdept.rename(columns = depttable.subdic[item],inplace=True)
        year_sdept.to_csv(filepos+depttable.namedic[item]+'SUB'+ext)



if __name__ == '__main__':
#    cleanmembertable()

#    print ('Merge Table begin')
#    MergeTable()
#    print ('Merge Table end')

    webtablefiles = {
#    2010:2010,2011:2011,2012:2012,
#    2013:2013,2014:2014,2015:2015,2016:(2016,'sales201601-12detail'),
    2017:'sales201701-12detail',2018:'sales201801-02detail'}
    postablefiles = {2011:'pos_2011',2012:'pos_2012',2013:'pos_2013',2014:'pos_2014',2015:'pos_2015',2016:'pos_2016',2017:'pos_2017'}
    postables = {}
    for year in postablefiles.keys():
        postables[year] = postable(postablefiles[year])

        

    
    shopn = shopname('shop')
    x_axix = [x for x in range(130)]

    usertable = UserTable('cleanutable')
    
    depttable = DEPTtable('HITRMD_DEPT')
    shoptable = shopname('shop')

#    Web analysis start

#    Web analysis end

    
    untable = postable('unified')
    

    data2017 = postables[2017]
    data2016 = postables[2016]
    data2015 = postables[2015]
    data2012 = postables[2012]
    

    print('start item analysis for 2017')
    [[itemM2017,itemF2017,itemMonth2017],[ShopM2017,ShopF2017,ShopMonth2017],shopItem2017] = Item(data2017,2017,usertable,depttable,shoptable)

    print('end item analysis for 2017')


    [[itemM2016,itemF2016,itemMonth2016],[ShopM2016,ShopF2016,ShopMonth2016],shopItem2016] = Item(data2016,2016,usertable,depttable,shoptable)

    [[itemM2015,itemF2015,itemMonth2015],[ShopM2015,ShopF2015,ShopMonth2015],shopItem2015] = Item(data2015,2015,usertable,depttable,shoptable)


    webtables = {}
    for year in webtablefiles.keys():
        print ('processinb sales of webtable for year '+str(year))
        ob = webtablefiles[year]
        if isinstance(ob,str):
            tb = ecbeingtable(ob)
        elif isinstance(ob,tuple):
            tb1 = genesistable(ob[0])
            tb2 = ecbeingtable(ob[1])
            tb = (tb1,tb2)
        else:
            tb = genesistable(ob)
        webtables[year] = tb
        print ('year '+str(year)+' end')

    print('Web Sales analysis start')
    SalesByAge17,CountByAge17 = GetSalesByAge(webtables[2017].table,usertable)    
    table = pd.DataFrame(index = x_axix,columns= [])
    table['SalesByAge17'] = SalesByAge17
    table['CountByAge17'] = CountByAge17
    table.to_csv(filepos+'WebSalesByAge'+ext)
    UserAnalysis(webtables[2017],usertable,shoptable,depttable)
    
    [[itemM2017,itemF2017,itemMonth2017],[ShopM2017,ShopF2017,ShopMonth2017],shopItem2017] = Item(webtables[2017],2017,usertable,depttable,shoptable)

    print('Web Sales analysis end')
    plt.bar(x_axix,SalesByAge17)
    plt.show()


    UserAnalysis(untable,usertable,shoptable,depttable)
#    UserAnalysis( postables[2011],usertable,shoptable,depttable)
#    RangeAnalysis(untable,usertable,shoptable)

    
    SDEPT_analysis(depttable)


    def IncreaseRatio(table1,table2):
        diffTable = table1-table2
        diffTable = diffTable/table2.astype('float')
        return(diffTable)
    IncreaseRatio

    diffShopItem = IncreaseRatio(shopItem2017,shopItem2016)
    diffShopMonth = IncreaseRatio(ShopMonth2017,ShopMonth2016)
    diffShopM = IncreaseRatio(ShopM2017,ShopM2016)
    diffShopF = IncreaseRatio(ShopF2017,ShopF2016)

    
    diffShopItem.to_csv(filepos+'diffShopItem1617'+ext)
    diffShopMonth.to_csv(filepos+'diffShopMonth1617'+ext)
    diffShopM.to_csv(filepos+'diffShopM1617'+ext)
    diffShopF.to_csv(filepos+'diffShopF1617'+ext)

    diffShopItem = IncreaseRatio(shopItem2016,shopItem2015)
    diffShopMonth = IncreaseRatio(ShopMonth2016,ShopMonth2015)
    diffShopM = IncreaseRatio(ShopM2016,ShopM2015)
    diffShopF = IncreaseRatio(ShopF2016,ShopF2015)
    
    diffShopItem.to_csv(filepos+'diffShopItem1516'+ext)
    diffShopMonth.to_csv(filepos+'diffShopMonth1516'+ext)
    diffShopM.to_csv(filepos+'diffShopM1516'+ext)
    diffShopF.to_csv(filepos+'diffShopF1516'+ext)



    ItemByItem(data2017.table,usertable,depttable)
    UserByAge(usertable.usertable)
    
    print ('start shop by year sales data creation')
    ShopSalesByYear(shopn,postables)
    print ('end shop by year sales data creation')
    


    DropIn17 = RecurringPurchaseCheck(data2012.table,data2017.table,usertable,PositiveCheck=False)
    plt.bar(x_axix,DropIn17)
    plt.show()
   

    
    SalesByAge17,CountByAge17 = GetSalesByAge(data2017.table,usertable)

    SalesByAge12,CountByAge12 = GetSalesByAge(data2012.table,usertable)



    SalesDiff = numpy.zeros(130)
    SalesDiff = SalesByAge17-SalesByAge12

    table = pd.DataFrame(index = x_axix,columns= [])
    table['SalesByAge17'] = SalesByAge17
    table['CountByAge17'] = CountByAge17
    table['SalesByAge12'] = SalesByAge12
    table['CountByAge12'] = CountByAge12
    table['Diff'] = SalesDiff
    table['DropIn17'] = DropIn17

    table.to_csv(filepos+'SalesByAge'+ext)


    plt.bar(x_axix,SalesByAge17)
    plt.show()
    
    plt.bar(x_axix,SalesByAge12)
    plt.show()
    
    plt.bar(x_axix,SalesDiff)
    plt.show()

    
    

