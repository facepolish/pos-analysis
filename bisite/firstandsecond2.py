from bi.posenv import depttablefile
import matplotlib.pyplot as plt
import pandas as pd
from datetime import timedelta,datetime,date
from numba import jit

posfile = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/bi/data/bi/pos.pkl'
userfile = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/bi/data/bi/user.pkl'
outfile = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/fands.xlsx'
outpath = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/'


#@jit
def set_freq (table):
    total_user_count = len(set(table.user_id))
    print("total user count is "+str(total_user_count))
    deptlist = set(table.DEPT)
    brandlist = set(table.brand)
    price_table = pd.DataFrame(0,index = deptlist,columns = deptlist)
    count_table = pd.DataFrame(0,index = deptlist,columns = deptlist)
    first_visit = pd.DataFrame(0,index = deptlist,columns = ['sales','count'])
    second_visit = pd.DataFrame(0, index=deptlist, columns=['sales', 'count'])

    brand_ptable  = pd.DataFrame(0,index = brandlist,columns = brandlist)
    brand_ctable = pd.DataFrame(0,index = brandlist,columns=brandlist)
    first_visitb = pd.DataFrame(0, index=brandlist, columns=['sales', 'count'])
    second_visitb = pd.DataFrame(0, index=brandlist, columns=['sales', 'count'])
#   forecastpowerprice = pd.DataFrame(0,index =deptlist,columns = deptlist )
 #   forecastpowercount = pd.DataFrame(0,index =deptlist,columns = deptlist )

    table = table.sort_values(by=['user_id','purchase_date'])

    cur_user = 0
    user_counter = 0
    visit_count = 0
    
    firstdeptset = set()
    firstbrandset = set()

    for ind,row in table.iterrows():
        user = row.user_id
        pdate = row.purchase_date
        dept = row.DEPT
        brand = row.brand
        if not(cur_user == user):
            cur_user = user
            visit_count = 1
            user_counter+=1
            last_visit_day = pdate
            firstdeptset = set()
            if user_counter%10000 == 0:
                print ("Now user count is "+str(user_counter))
#                if user_counter>=100000:
#                    break
        if visit_count>2:
            continue
        if not (last_visit_day == pdate):
            visit_count+=1
            last_visit_day = pdate
        if visit_count == 1:
            first_visit.loc[dept,'sales']+=row.price
            first_visit.loc[dept,'count']+=1
            first_visitb.loc[brand,'sales']+=row.price
            first_visitb.loc[brand,'count']+=1
            firstdeptset.add(dept)
            firstbrandset.add(brand)
        elif visit_count == 2:
            second_visit.loc[dept,'sales']+=row.price
            second_visit.loc[dept,'count']+=1
            second_visitb.loc[brand,'sales']+=row.price
            second_visitb.loc[brand,'count']+=1
            for dept1 in firstdeptset:
                price_table.loc[dept1,dept]+=row.price
                count_table.loc[dept1,dept]+=1
            for brand1 in firstbrandset:
                brand_ptable.loc[brand1,brand]+=row.price
                brand_ctable.loc[brand1,brand]+=1

    price_table.loc[:, '0'] = 0
    count_table.loc[:, '0'] = 0
    price_table.loc[:, '-1'] = 0
    count_table.loc[:, '-1'] = 0

    brand_ptable.loc[:,'0'] = 0
    brand_ctable.loc[:,'0'] = 0
    brand_ptable.loc[:,'-1'] = 0
    brand_ctable.loc[:,'-1'] = 0
    for dept in deptlist:
        price_table.loc[dept,'0'] = sum(price_table.loc[dept,:])
        count_table.loc[dept,'0'] = sum(count_table.loc[dept,:])
        price_table.loc[dept,'-1'] = first_visit.loc[dept,'sales']
        count_table.loc[dept, '-1'] = first_visit.loc[dept, 'count']
    for dept in deptlist:
        price_table.loc['0',dept] = second_visit.loc[dept,'sales']
        count_table.loc['0',dept] = second_visit.loc[dept,'count']
    brand_ptable.loc[:,'0'] = 0
    brand_ctable.loc[:,'0'] = 0
    brand_ptable.loc[:,'-1'] = 0
    brand_ctable.loc[:,'-1'] = 0
    for brand in brandlist:
        brand_ptable.loc[brand,'0'] = sum(brand_ptable.loc[brand,:])
        brand_ctable.loc[brand,'0'] = sum(brand_ctable.loc[brand,:])
        brand_ptable.loc[brand,'-1'] = first_visitb.loc[brand,'sales']
        brand_ctable.loc[brand, '-1'] = first_visitb.loc[brand, 'count']
    for brand in brandlist:
        brand_ptable.loc['0',brand] = second_visitb.loc[brand,'sales']
        brand_ctable.loc['0',brand] = second_visitb.loc[brand,'count']


    price_table = price_table.sort_index(axis = 1)
    count_table = count_table.sort_index(axis = 1)
    brand_ptable = brand_ptable.sort_index(axis = 1)
    brand_ctable = brand_ctable.sort_index(axis = 1)
    return(price_table,count_table,brand_ptable,brand_ctable)


if __name__=='__main__':
    def cnv_deptlabel(table):
        table.columns = [int(x) for x in table.columns]
        table.index = [int(x) for x in table.index]
        return(table)
    zerodic = {-1:'初回計',0:'２回目合計'}

    depdic = pd.read_pickle(depttablefile)
    depdic.update(zerodic)

    postable = pd.read_pickle(posfile)
    postable = postable.reset_index()
    user = pd.read_pickle(userfile)
    user = user.reset_index()
    user.registered_date = [datetime.strptime(x,'%Y%m%d') for x in user.registered_date]


    begindate = pd.Timestamp(2018,12,1)
#    begindate = pd.Timestamp(2018,12,1)
#    enddate =  pd.Timestamp(2018,12,30)
    enddate =  pd.Timestamp(2019,12,31)
    postable = postable[postable.purchase_date >= begindate]
    postable = postable[postable.purchase_date <= enddate]

    target_users = user[user.registered_date>=begindate]
    target_users = target_users[target_users.registered_date<=enddate]
    target_user_set = set(target_users.user_id)
    print ("registered user count = "+str(len(target_user_set)))
    pos_target = postable[postable.user_id.isin(target_user_set)]

    ret1,ret2,ret3,ret4 = set_freq(pos_target)
    ret1 = cnv_deptlabel(ret1)
    ret2 = cnv_deptlabel(ret2)
    ret1 = ret1.rename(columns=depdic,index=depdic)
    ret2 = ret2.rename(columns=depdic,index=depdic)
    ret3 = ret3.rename(columns=zerodic,index=zerodic)
    ret4 = ret4.rename(columns=zerodic,index=zerodic)

    ret1.to_excel(outpath+'price1.xlsx')
    ret2.to_excel(outpath+'count1.xlsx')
    ret3.to_excel(outpath+'brandprice1.xlsx')
    ret4.to_excel(outpath+'brandcount1.xlsx')


    pos_target2 = postable
    rest_users = set(pos_target2.user_id) - target_user_set
    pos_target2 = pos_target2[pos_target2.user_id.isin(rest_users)]
    
    ret1,ret2,ret3,ret4 = set_freq(pos_target2)
    ret1 = cnv_deptlabel(ret1)
    ret2 = cnv_deptlabel(ret2)
    ret1 = ret1.rename(columns=depdic,index=depdic)
    ret2 = ret2.rename(columns=depdic,index=depdic)
    ret3 = ret3.rename(columns=zerodic,index=zerodic)
    ret4 = ret4.rename(columns=zerodic,index=zerodic)

    ret1.to_excel(outpath+'price2.xlsx')
    ret2.to_excel(outpath+'count2.xlsx')
    ret3.to_excel(outpath+'brandprice2.xlsx')
    ret4.to_excel(outpath+'brandcount2.xlsx')
    

    pos_target3 = postable

    ret1,ret2,ret3,ret4 = set_freq(pos_target3)
    ret1 = cnv_deptlabel(ret1)
    ret2 = cnv_deptlabel(ret2)
    ret1 = ret1.rename(columns=depdic,index=depdic)
    ret2 = ret2.rename(columns=depdic,index=depdic)
    ret3 = ret3.rename(columns=zerodic,index=zerodic)
    ret4 = ret4.rename(columns=zerodic,index=zerodic)

    ret1.to_excel(outpath+'price3.xlsx')
    ret2.to_excel(outpath+'count3.xlsx')
    ret3.to_excel(outpath+'brandprice3.xlsx')
    ret4.to_excel(outpath+'brandcount3.xlsx')



