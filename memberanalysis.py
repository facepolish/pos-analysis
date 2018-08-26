from tableclass import UserTable,UserByAge,postable,GetSalesByAge,Item,DEPTtable,shopname,Item3
import os
import datetime

import openpyxl as xl
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


usertablefile = 'cleanutable'
postablefile = 'pos_2017'
postable_unified = 'unified'

filepos = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/output/'


if __name__ == '__main__':

    def convtonum (year,month):
        return(12*(year - 2011)+month-1)
    agelist = [x for x in range(130)]
    genderlist = [0,1,2]
    genderdic = {1:'male',2:'female',0:'unkown'}
    countlist = [0,1]
    countdic = {0:'New',1:'Ex'}

    YearMonthList = [x for x in range(85)]
    YearMonthListDic = {x:str(2011+int(x/12))+u'年'+str(x%12+1)+u'月' for x in range(85)}
    dept = DEPTtable('HITRMD_DEPT')
    shopn = shopname('shop')
    ut = UserTable(usertablefile)
    usertable = ut.usertable

    pt = postable(postable_unified)
    posall = pt.table
    deptlist = list(set(dept.depttable.DEPT))
    shoplist = list(set(shopn.shopname_table.index))
    pos156 = posall[posall.shop == 156]
    shopped156 = set(pos156.user_id)
    shoped156pos = posall[posall.user_id.isin(shopped156)]
    shoped156pos = shoped156pos.sort_values(by = ['user_id','purchase_date'])
    shopped156shop = pd.DataFrame(0,index = YearMonthList,columns = shoplist)
    counter = 0
    totalcount = shoped156pos.shape[0]
    for ind,row in shoped156pos.iterrows():
        counter+=1
        if counter%100000 == 0:
            per = counter/totalcount
            print ("Now "+str(counter)+"  "+str(per)+"%")
        yr = row.purchase_date.year
        mn = row.purchase_date.month
        
        shopped156shop.loc[convtonum(yr,mn),row.shop]+= row.price
    shopped156shop.rename(index = YearMonthListDic,columns = shopn.namedic,inplace = True)
    shopped156shop.to_csv(filepos+'shopped156shop.csv')
    
    '''
    
    
    DateCount = pd.DataFrame(0,index = YearMonthList,columns =countlist)
    DateItemNew = pd.DataFrame(0,index = YearMonthList,columns = deptlist)
    DateItemEx = pd.DataFrame(0,index = YearMonthList,columns = deptlist)
    DateAgeNew = pd.DataFrame(0,index = YearMonthList,columns = agelist)
    DateAgeEx = pd.DataFrame(0,index = YearMonthList,columns = agelist)
    DateGenderNew = pd.DataFrame(0,index = YearMonthList,columns = genderlist)
    DateGenderEx = pd.DataFrame(0,index = YearMonthList,columns = genderlist)

    pos156 = pos156.sort_values(by = ['user_id','purchase_date'])
    ex_userset = set(pos156.user_id) - set(usertable.index)
    counter = 0
    totalcount = pos156.shape[0]
    current_user = 0
    lastyr = 0
    lastmn = 0
    lastd = 0
    for ind ,row in pos156.iterrows():
        counter+=1
        if counter%100000 == 0:
            per = counter/totalcount
            print ("Now "+str(counter)+"  "+str(per)+"%")
        if not(current_user == row.user_id):
            current_user = row.user_id
            if current_user in ex_userset:
                reg_year = 0
                reg_month = 0
                age = 0
                gender = 0
            else:
                reg_date = usertable.loc[current_user,'registered_date']
                reg_year = reg_date.year
                reg_month = reg_date.month
                age = usertable.loc[current_user,'age']
                if usertable.loc[current_user,'gender'] == u'男性':
                    gender = 1
                else:
                    gender = 2
        yr = row.purchase_date.year
        mn = row.purchase_date.month
        dd = row.purchase_date.day

        if yr == reg_year and mn == reg_month:
            dat = convtonum(yr,mn)
            DateItemNew.loc[dat,row.DEPT]+= row.price
            DateAgeNew.loc[dat,age] += row.price
            DateGenderNew.loc[dat,gender] += row.price
            NewFlag = True
        else:
            dat = convtonum(yr,mn)
            DateItemEx.loc[dat,row.DEPT]+= row.price
            DateAgeEx.loc[dat,age] += row.price
            DateGenderEx.loc[dat,gender] += row.price
            NewFlag = False
        if not(yr == lastyr and mn == lastmn and dd == lastd):
            lastyr = yr
            lastmn = mn
            lastd = dd
            if NewFlag == True:
                DateCount.loc[dat,0]+=1
            else:
                DateCount.loc[dat,1]+=1
            
            

    DateItemNew.rename(index = YearMonthListDic,columns = dept.namedic, inplace = True)
    DateItemEx.rename(index = YearMonthListDic,columns = dept.namedic, inplace = True)
    DateItemNew.to_csv(filepos+'DateItemNew156.csv')
    DateItemEx.to_csv(filepos+'DateItemEx156.csv')
    DateAgeNew.rename(index = YearMonthListDic,inplace = True)
    DateAgeNew.to_csv(filepos+'DataAgeNew156.csv')
    DateAgeEx.rename(index = YearMonthListDic,inplace = True)
    DateAgeEx.to_csv(filepos+'DataAgeEx156.csv')

    DateGenderEx.rename(index = YearMonthListDic,columns = genderdic,inplace = True)
    DateGenderEx.to_csv(filepos+'DateGenderEx156.csv')
    DateGenderNew.rename(index = YearMonthListDic,columns = genderdic,inplace = True)
    DateGenderNew.to_csv(filepos+'DateGenderNew156.csv')
    
    DateCount.rename(index = YearMonthListDic,columns = countdic,inplace = True)
    DateCount.to_csv(filepos+'DateCount156.csv')



    dayslist1 = ['30','60','90']
    dayslist2 = ['0','1','2','3','4','5','6','7']
    agelist = [x for x in range(130)]
    yearlist = ['all','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017','2018']



    
    monthlist = [1,2,3,4,5,6,7,8,9,10,11,12]
    uage = pd.DataFrame(0,index = agelist,columns = yearlist )
    uageMale = pd.DataFrame(0,index = agelist,columns = yearlist )
    uageFemale = pd.DataFrame(0,index = agelist,columns = yearlist )

    ex_userset = set(posall.user_id) - set(usertable.index)

#    posall = posall[posall.user_id.isin(set(usertable.index))]
    posall = posall.sort_values(by=['user_id','purchase_date'])
    total_pos_count = posall.shape[0]
    current_user = 0
    
    YewrShopNew = pd.DataFrame(0,index = yearlist,columns = shoplist)
    YewrShopEx = pd.DataFrame(0,index = yearlist,columns = shoplist)
    YewrShopDrop = pd.DataFrame(0,index = yearlist,columns = shoplist)


    counter = 0
    totalcount = posall.shape[0]
    for ind ,row in posall.iterrows():
        counter+=1
        if counter%100000 == 0:
            per = counter/totalcount
            print ("Now "+str(counter)+"  "+str(per)+"%")
        if not(current_user == row.user_id):
            current_user = row.user_id
            dropflag = False
            if current_user in ex_userset:
                dropflag = True
            else:
                reg_date = usertable.loc[current_user,'registered_date']
                reg_year = reg_date.year
        purchase_year = row.purchase_date.year
        if dropflag == True:
            YewrShopDrop.loc[str(purchase_year),row.shop]+=row.price
        elif reg_year == purchase_year:
            YewrShopNew.loc[str(purchase_year),row.shop]+=row.price
        else:
            YewrShopEx.loc[str(purchase_year),row.shop]+=row.price
    YewrShopNew.rename(columns = shopn.namedic,inplace = True)
    YewrShopEx.rename(columns = shopn.namedic,inplace = True)
    YewrShopDrop.rename(columns = shopn.namedic,inplace = True)

    YewrShopNew.to_csv(filepos+'YearShopNew.csv')
    YewrShopEx.to_csv(filepos+'YearShopEx.csv')
    YewrShopDrop.to_csv(filepos+'YearShopDrop.csv')



    counter = 0
    totalcount = usertable.shape[0]
    for u,row in usertable.iterrows():
        counter+=1
        if counter%1000 == 0:
            per = counter/totalcount
            print ("Now "+str(counter)+"  "+str(per)+"%")
        u_age = row.age
        reg_year = row.registered_date.year
        u_age += reg_year -2017
        if u_age <0 or u_age>=130:
            u_age = 0  # Abnormal age set age as 0
        uage.loc[u_age,'all']+=1
        if row.gender == u'男性':
            uageMale.loc[u_age,'all']+=1
        else:
            uageFemale.loc[u_age,'all']+=1

        if reg_year <2005 or reg_year > 2018:
            print (row)
            continue
        uage.loc[u_age,str(reg_year)]+=1
        if row.gender == u'男性':
            uageMale.loc[u_age,str(reg_year)]+=1
        else:
            uageFemale.loc[u_age,str(reg_year)]+=1

    plt.bar(agelist,uage.loc[:,'all'])
    plt.show()
    plt.bar(agelist,uage.loc[:,'2017'])
    plt.show()
    uage.to_csv(filepos+'memberage.csv')
    uageMale.to_csv(filepos+'memberageMale.csv')
    uageFemale.to_csv(filepos+'memberageFemale.csv')
        
        
    
    
    pt = postable(postablefile)
    posall = pt.table
#    posall = posall[posall.user_id.isin(set(usertable.index))]
    posall = posall.sort_values(by=['user_id','purchase_date'])
    total_pos_count = posall.shape[0]

    excludeset = set(posall.user_id) - set(usertable.index)
    current_user = 0
    counter = 0
    monthlysales1 = pd.DataFrame(0,index = ['new','existing'],columns = monthlist,)
    monthshopnew = pd.DataFrame(0,index = monthlist,columns = shoplist)
    monthshopex = pd.DataFrame(0,index = monthlist,columns = shoplist)
    for ind, row in posall.iterrows():
        counter+=1
        if counter%1000 == 0:
            per = counter/total_pos_count
            print ("Now "+str(counter)+"  "+str(per)+"%")
        if not(current_user == row.user_id):
            current_user = row.user_id
            if row.user_id in excludeset:
                reg_month = 0
            else:
                rd = usertable.loc[current_user,'registered_date']
                if rd.year == 2017:
                    reg_month = rd.month
                else:
                    reg_month = 0
        thismonth = row.purchase_date.month
        if thismonth == reg_month:
            monthlysales1.loc['new',thismonth]+= row.price
            monthshopnew.loc[thismonth,row.shop]+= row.price
        else:
            monthlysales1.loc['existing',thismonth]+= row.price
            monthshopex.loc[thismonth,row.shop]+= row.price
            
    monthlysales1.to_csv(filepos+'new_existing.csv')
    monthshopnew.rename(columns = shopn.namedic,inplace = True)
    monthshopex.rename(columns = shopn.namedic,inplace = True)
    monthshopnew.to_csv(filepos+'monthshopnew.csv')
    monthshopex.to_csv(filepos+'monthshopex.csv')







    targetdate = (datetime.datetime(2017,2,1),datetime.datetime(2017,8,1))
    print("target user selection starts")
    mask = (usertable.registered_date >= targetdate[0]) & (usertable.registered_date <= targetdate[1])
    targetusers = usertable[mask]
    print("target user selection end")

    
    print("target pos selection starts")
    mask2 = posall.user_id.isin(set(targetusers.index))
    print ("mask creation end")

    targetpos = posall[mask2]
    targetpos = targetpos.sort_values(by=['user_id','purchase_date'])
    print("target pos selection end")
    total_pos_count = targetpos.shape[0]
    print ("pos data count is "+str(total_pos_count))
    userlist = list(set(targetpos.user_id))
    

    initial_purchase = pd.DataFrame(0,index = userlist,columns = dayslist1 )
    initial_purchase2 = pd.DataFrame(0,index = userlist,columns = dayslist2 )
    item1 = pd.DataFrame(0,index = dayslist1,columns = deptlist)
    item2 = pd.DataFrame(0,index = dayslist2,columns = deptlist)
    shop1 = pd.DataFrame(0,index = dayslist1,columns = shoplist)
    shop2 = pd.DataFrame(0,index = dayslist2,columns = shoplist)
    
#    ['first_visit','second_visit','third_visit','first_30days','30to60days','61to90days']
    
    current_user = 0
    counter = 0
    
    for user,row in targetpos.iterrows():
        counter+=1
        if counter%1000 == 0:
            per = counter/total_pos_count
            print ("Now "+str(counter)+"  "+str(per)+"%")
        if not(current_user == row.user_id):
            current_user = row.user_id
            skipflag1 = False
            skipflag2 = False
            days = np.zeros(len(dayslist2))
            days[0] = (row.purchase_date - targetdate[0]).days
            stage = 0
            stage2 = 0
            upperday = 30
        if (skipflag1 == True) and (skipflag2 == True):
            continue
        daydiff = (row.purchase_date - targetdate[0]).days - days[0]
        
        if daydiff <= upperday:
            dayrange = str(upperday)
            initial_purchase.loc[current_user,dayrange]+= row.price
            item1.loc[dayrange,row.DEPT]+=row.price
            shop1.loc[dayrange,row.shop]+=row.price
        else:
            if stage2 == 2:
                skipflag1 = True
            else:
                stage2+=1
                upperday = int(30+30*stage2)
        daydiff2 = (row.purchase_date - targetdate[0]).days - days[stage]
        if not(daydiff2 == 0):
            if stage == 7:
                skipflag2 = True
                continue
            else:
                stage+=1
        ds = str(stage)
        initial_purchase2.loc[current_user,ds]+=row.price
        item2.loc[ds,row.DEPT] += row.price
        shop2.loc[ds,row.shop]+=row.price

    maxdhist = pd.DataFrame(0,index = dayslist2,columns = ['count'])


    print (item1.head(4))
    item1.rename(columns = dept.namedic,inplace = True)
    print (item1.head(4))
    print (item2.head(4))
    item2.rename(columns = dept.namedic,inplace = True)
    print (item2.head(4))
    shop1.rename(columns = shopn.namedic,inplace = True)
    shop2.rename(columns = shopn.namedic,inplace = True)
        
    item1.to_csv(filepos+'initial_items1.csv')
    item2.to_csv(filepos+'initial_items2.csv')

    shop1.to_csv(filepos+'initial_shop1.csv')
    shop2.to_csv(filepos+'initial_shop2.csv')

    num_user = len(userlist)
    sum1 = sum(initial_purchase.loc[:,'30'])
    print ('first 30 days average  = '+str(sum1/num_user))
    sum2 = sum(initial_purchase.loc[:,'60'])
    print ('30 to 60 days average  = '+str(sum2/num_user))
    sum3 = sum(initial_purchase.loc[:,'90'])
    print ('60 to 90 days average  = '+str(sum3/num_user))

    sum1 = sum(initial_purchase2.loc[:,'0'])
    print ('first  day average  = '+str(sum1/num_user))
    sum2 = sum(initial_purchase2.loc[:,'1'])
    print ('Second day average  = '+str(sum2/num_user))
    sum3 = sum(initial_purchase2.loc[:,'2'])
    print ('Third day average  = '+str(sum3/num_user))
    sum3 = sum(initial_purchase2.loc[:,'3'])
    print ('Third day average  = '+str(sum3/num_user))
    sum3 = sum(initial_purchase2.loc[:,'4'])
    print ('Third day average  = '+str(sum3/num_user))
    sum3 = sum(initial_purchase2.loc[:,'5'])
    print ('Third day average  = '+str(sum3/num_user))
    sum3 = sum(initial_purchase2.loc[:,'6'])
    print ('Third day average  = '+str(sum3/num_user))
    sum3 = sum(initial_purchase2.loc[:,'7'])
    print ('Third day average  = '+str(sum3/num_user))


    '''


   
