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

　   標準モデルとの差（年齢、地域、性別）

'''
from tableclass import UserTable,UserByAge,postable,GetSalesByAge

import openpyxl as xl
import pandas as pd
import numpy as np

fileinputpos = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/input/data180606/'

inputfile = u'おとな女子登山部名簿'
inputfile2 = u'登山学校名簿'
climbsheet = u'登山学校名簿'

ext = '.xlsx'
sheets = ['201603','201703','201803']
colnamedic = {u'好日山荘メンバーズカード番号':'user_id',u'会員番号':'user_id'}
usertablefile = 'cleanutable'
postablefile = 'pos_2017'

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

if __name__ == '__main__':
    cs = pd.read_excel(fileinputpos+inputfile2+ext,climbsheet)
    cs.rename(columns = colnamedic,inplace = True)
    climbschoolmemberlist = cs.user_id
    climbschoolmemberlist = [str(i) for i in climbschoolmemberlist]



    '''
    おとな女子登山部名簿　読み込み。－＞会員番号リスト作成
    '''
    memberlist = []
    for sn in sheets:
        st = pd.read_excel(fileinputpos+inputfile+ext,sn)
        st.rename(columns =colnamedic,inplace = True)
#        print (st.head(20))
        print ("user count for "+str(sn)+'is '+str(len(st.user_id)))
        memberlist.extend(st.user_id)
    print ('total count is '+str(len(memberlist)))
    memberlist = [str(i) for i in memberlist]

    ut = UserTable(usertablefile)
    allusers = ut.usertable
    
    cs_users = allusers[allusers.index.isin(climbschoolmemberlist)]
#    memberlist = list(set(allusers.index) & set(memberlist))

#    subusers = allusers[memberlist]
#    subusers = allusers.where(allusers.user_id.isin(memberlist)).dropna()
    subusers = allusers[allusers.index.isin(memberlist)]
    print (subusers.head(20))
    
    UserByAge(cs_users,'climb_sc_')
    UserByAge(subusers,'otona_')
    UserByAge(allusers,'all_')
    
    pt = postable(postablefile)
    posall = pt.table
    
    pos_cs = posall[posall.user_id.isin(climbschoolmemberlist)]
    pos_otona = posall[posall.user_id.isin(memberlist)]

    purchaser_count_cs = len(set(pos_cs.user_id))
    purchaser_count = len(set(pos_otona.user_id))

    cs_sales_by_age, cs_count_by_age = GetSalesByAge(pos_cs,allusers)
    cs_sum = sum(cs_sales_by_age)
    cs_sales_per_person = sdiv(cs_sales_by_age,cs_count_by_age)
    print('Climbing Scheel Sales per person = '+str(float(cs_sum)/purchaser_count_cs))
    


    otona_sales_by_age, otona_count_by_age = GetSalesByAge(pos_otona,allusers)
    otona_sum = sum(otona_sales_by_age)
    otona_sales_per_person = sdiv(otona_sales_by_age,otona_count_by_age)
    print('Otona Jyoshi Sales per person = '+str(float(otona_sum)/purchaser_count))
    
    all_purchaser_count = len(set(posall.index))
    
    all_sales_by_age ,all_count_by_age = GetSalesByAge(posall,allusers,'Female')
    all_sum = sum(all_sales_by_age)
    all_sales_per_person = sdiv(all_sales_by_age,all_count_by_age)
    print('all Sales per person = '+str(float(all_sum)/all_purchaser_count))

    adjusted_all_sales_by_age = smul(all_sales_per_person,otona_count_by_age)
    adjusted_sum = sum(adjusted_all_sales_by_age)
    print('All Adjusted per person sales with Otona Jyoshi = '+str(float(adjusted_sum)/purchaser_count))

    print ("Otona Ratio = "+str(otona_sum/adjusted_sum))


    
    

