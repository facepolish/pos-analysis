'''
　予定機能
　集団属性
　
　   年齢分布
　   性別分布
　   地域分布

　   平均購買金額
　   購入物品の特性
　   購入日の偏り

　   来店特性
     　   曜日の偏り
　        時間帯の偏り
　   購入ブランド特性のズレ
　   
　   登録者と企画参加者（エンゲージメントの影響継続度）

　   標準モデルとの差（年齢、地域、性別）

'''
from tableclass import UserTable,UserByAge,postable,GetSalesByAge,Item,DEPTtable,shopname,Item3
import os
import datetime

import openpyxl as xl
import pandas as pd
import numpy as np

fileinputpos = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/input/data180606/'

inputfile = u'おとな女子登山部名簿'
inputfile2 = u'登山学校名簿'
dutyfreetablefile = u'免税販売明細'
climbsheet = u'登山学校名簿'
dfsheet = u'免税'

ext = '.xlsx'
colnamedic = {
     u'好日山荘メンバーズカード番号':'user_id',
     u'会員番号':'user_id',
     u'店舗ｺｰﾄﾞ':'shop',
     u'売上日付':'purchase_date',
     u'売上額':'price',
     u'POS販売時刻':'purchase_time',
     u'売上伝票番号':'slip_id'}
usertablefile = 'cleanutable'
postablefile = 'pos_2017'

#@jit


def sdiv(a,b):
    size = min(a.shape[0],b.shape[0])
    res = np.zeros([size])
    for i in range(size):
        if not b[i] == 0:
            res[i] = a[i]/b[i]
        else:
            res[i] = 0
    return(res)

def smul (a,b):
    size = min(a.shape[0],b.shape[0])
    res = np.zeros([size])
    for i in range(size):
        res[i] = a[i]*b[i]
    return(res)

def ClimbingSchoolMembers():
    cs = pd.read_excel(fileinputpos+inputfile2+ext,climbsheet)
    cs.rename(columns = colnamedic,inplace = True)
    climbschoolmemberlist = cs.user_id
    climbschoolmemberlist = [str(i) for i in climbschoolmemberlist]
    
    return(climbschoolmemberlist)

def DutyFreeTable():
    cs = pd.read_excel(fileinputpos+dutyfreetablefile+ext,dfsheet)
    cs.rename(columns = colnamedic,inplace = True)
    cs.purchase_date = pd.to_datetime(cs.purchase_date, format='%Y%m%d')
    cs = cs.set_index('purchase_date')
    cs = cs[cs.index.year == 2017]
    cs = cs.reset_index()

    
    return(cs)

    
def OtonaJyoshiMembers(TargetYears):
    memberlist = []
    for sn in TargetYears:
        st = pd.read_excel(fileinputpos+inputfile+ext,sn)
        st.rename(columns =colnamedic,inplace = True)
#        print (st.head(20))
        print ("user count for "+str(sn)+'is '+str(len(st.user_id)))
        memberlist.extend(st.user_id)
#    member2018 = st.user_id
#    member2018 = [str(i) for i in member2018]

    print ('total count is '+str(len(memberlist)))
    memberlist = [str(i) for i in memberlist]
    return(memberlist)
    
def SalesByAge(postable,usertable):
    purchased_mem_count = len(set(postable.user_id))
    sales_age, count_age = GetSalesByAge(postable,usertable)
    total_sales = sum(sales_age)
    mean_sales_age = sdiv(sales_age,count_age)
    mean_sales = total_sales/purchased_mem_count
    return( sales_age, count_age,mean_sales_age,mean_sales,purchased_mem_count)

#@jit
def Item2(datatable,year,shopn,prefix = 'pos'):
    filepos = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/output/'
    fileprefix = filepos+prefix
    ysext = str(year)+'.csv'
    target_file = fileprefix+'SalesByDays'+ysext
    if os.path.exists(target_file):
        return
    
    min_date = min(datatable.purchase_date)
    max_date = max(datatable.purchase_date)
    day_count = (max_date-min_date).days
    day_serial = [i for i in range(day_count+1)]
    day_dic = {i:(min_date+datetime.timedelta(days = i)) for i in range(day_count+1) }

    daily_sales = pd.DataFrame(0,index = ['Sales'],columns = day_serial)

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
        day_diff = thisrow.purchase_date - min_date
        daily_sales.loc['Sales',int(day_diff.days)] += thisrow.price
    
    daily_sales.rename(columns = day_dic,inplace = True)
    daily_sales.to_csv(target_file)
    return(daily_sales)



if __name__ == '__main__':


    climbschoolmemberlist = ClimbingSchoolMembers()
    '''
    おとな女子登山部名簿　読み込み。－＞会員番号リスト作成
    '''
    sheets = ['201603','201703','201803']

    memberlist = OtonaJyoshiMembers(sheets)

    dual_mem  = list(set(climbschoolmemberlist) & set(memberlist))

    dual_ratio = float(len(dual_mem))/ len(set(memberlist))
    print ("dual ratio = "+str(dual_ratio))


    member2018 = OtonaJyoshiMembers(['201803'])

    ut = UserTable(usertablefile)
    dept = DEPTtable('HITRMD_DEPT')
    shopn = shopname('shop')
    
    cs = DutyFreeTable()
    Item3(cs,2017,dept,shopn)
    
    

    allusers = ut.usertable
    UserByAge(allusers,'all_')
    
    cs_users = allusers[allusers.index.isin(climbschoolmemberlist)]
    UserByAge(cs_users,'climb_sc_')

    subusers = allusers[allusers.index.isin(memberlist)]
    UserByAge(subusers,'otona_')


    print (subusers.head(20))
    
    
    pt = postable(postablefile)
    posall = pt.table
    print("item analysis start")
    ret = Item(posall,2017,allusers,dept,shopn,'all_')
#    ret = Item2(posall,2017,shopn,'all_')


    o_pos = posall[posall.user_id.isin(memberlist)]    
    ret = SalesByAge(o_pos,allusers)
    print('Otona Jyoshi Sales per person = '+str(ret[3]))
    otona_count_by_age = ret[1]
    purchaser_count = ret[4]
    otona_sale_by_age = ret[0]
    otona_sum = sum(otona_sale_by_age)
    ret = Item(o_pos,2017,allusers,dept,shopn,'otona_')

    
    cl_pos = posall[posall.user_id.isin(climbschoolmemberlist)]    
    ret = SalesByAge(cl_pos,allusers)
    print('Climbing Scheel Sales per person = '+str(ret[3]))
    ret = Item(cl_pos,2017,allusers,dept,shopn,'climb_sc_')


    o18_pos = posall[posall.user_id.isin(member2018)]    
    ret = SalesByAge(o18_pos,allusers)
    print('Otona Jyoshi 2018 Sales per person in 2017 = '+str(ret[3]))
    
#    all_purchaser_count = len(set(posall.index))
    
    all_sales_by_age ,all_count_by_age = GetSalesByAge(posall,allusers,'Female')
    all_sum = sum(all_sales_by_age)
    all_purchaser_count = sum(all_count_by_age)
    all_sales_per_person = sdiv(all_sales_by_age,all_count_by_age)
    print('Female all Sales per person = '+str(float(all_sum)/all_purchaser_count))

    adjusted_all_sales_by_age = smul(all_sales_per_person,otona_count_by_age)
    adjusted_sum = sum(adjusted_all_sales_by_age)
    print('All Adjusted per person sales with Otona Jyoshi = '+str(float(adjusted_sum)/purchaser_count))


    print ("Otona Ratio = "+str(otona_sum/adjusted_sum))


    
    

