from bi.posenv import depttablefile
from bi.posenv import sdepttablefile
#from statistics import mean,median,div
#import matplotlib.pyplot as plt
import pandas as pd
from datetime import timedelta,datetime,date
from numba import jit

posfile = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/bi/data/bi/pos.pkl'
userfile = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/bi/data/bi/user.pkl'
outfile = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/fands.xlsx'
outpath = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/'

deepenlist = ['01', '02', '18', '19']

def index_tuple (table,sdeptdic):
    deptset = set(table.DEPT)
    tuplelist = []
    for dept in deptset:
        if dept in deepenlist:
            sdepttable = table[table.DEPT == dept]
            sdeptset = set(sdepttable.SDEPT)
            for sdept in sdeptset:
                tuplelist.append((dept,sdeptdic[int(dept)][int(sdept)]))
        else:
            tuplelist.append((dept,''))
    return (tuplelist)

def top_users(table,ratio):
    maxdate = max(table.purchase_date)
    print ("max date = "+str(maxdate))
    recit_table = table.groupby("slip_id").sum()
    print("レジカウント　＝　"+str(recit_table.shape[0]))
    print("合計　= " +"{:,}".format(recit_table.price.sum()) +" 平均　＝　"+"{:,.2f}".format(recit_table.price.mean())+" 中央値　=　"+"{:,.2f}".format(recit_table.price.median())+"  標準偏差 = "+str(recit_table.price.std()))
    sum_table = table.groupby("user_id").sum()
    print("合計　= " +"{:,}".format(sum_table.price.sum()) +" 平均　＝　"+"{:,.2f}".format(sum_table.price.mean())+" 中央値　=　"+"{:,.2f}".format(sum_table.price.median())+"  標準偏差 = "+str(sum_table.price.std()))
    sum_table = sum_table.sort_values(by="price", ascending=False)
    total_count = sum_table.shape[0]
    top_count = int(total_count*ratio)
    print ("sales of  top user is "+str(sum_table.ix[0,"price"]))
    print ("sales of  "+str(top_count)+" user is "+str(sum_table.ix[top_count,"price"]))
    users = sum_table.index[0:top_count]
    new_table = table[table.user_id.isin(users)]
    return(new_table)
#@jit
def set_freq (table,sdeptdic,strdeptdic,zerodic):
    total_user_count = len(set(table.user_id))
    print("total user count is "+str(total_user_count))
    deptsdepttuple = index_tuple(table,sdeptdic)
    multi = pd.MultiIndex.from_tuples(deptsdepttuple, names=['DEPT', 'SDEPT'])
    brandlist = set(table.brand)
    price_table = pd.DataFrame(0,index = multi,columns = multi)
    count_table = pd.DataFrame(0,index = multi,columns = multi)
    first_visit = pd.DataFrame(0,index = multi,columns = ['sales','count'])
    second_visit = pd.DataFrame(0, index=multi, columns=['sales', 'count'])

    brand_ptable  = pd.DataFrame(0,index = brandlist,columns = brandlist)
    brand_ctable = pd.DataFrame(0,index = brandlist,columns=brandlist)
    first_visitb = pd.DataFrame(0, index=brandlist, columns=['sales', 'count'])
    second_visitb = pd.DataFrame(0, index=brandlist, columns=['sales', 'count'])
#   forecastpowerprice = pd.DataFrame(0,index =deptlist,columns = deptlist )
 #   forecastpowercount = pd.DataFrame(0,index =deptlist,columns = deptlist )


#    return(price_table,count_table,brand_ptable,brand_ctable)

    table = table.sort_values(by=['user_id','purchase_date'])

    cur_user = 0
    user_counter = 0
    visit_count = 0
    
    firstdeptset = set()
    firstbrandset = set()

    for ind,row in table.iterrows():
        user = row.user_id
        pdate = row.purchase_date
        if (row.DEPT in deepenlist):
            deptsdept = (row.DEPT,sdeptdic[int(row.DEPT)][int(row.SDEPT)])
        else:
            deptsdept = (row.DEPT,"")
        brand = row.brand
        if not(cur_user == user):
            cur_user = user
            visit_count = 1
            user_counter+=1
            last_visit_day = pdate
            firstdeptset = set()
            firstbrandset = set()
            if user_counter%1000 == 0:
                print ("Now user count is "+str(user_counter))
#                if user_counter>=100000:
#                    break
        if visit_count>2:
            continue
        if not (last_visit_day == pdate):
            visit_count+=1
            last_visit_day = pdate
        if visit_count == 1:
            first_visit.loc[deptsdept,'sales']+=row.price
            first_visit.loc[deptsdept,'count']+=1
            first_visitb.loc[brand,'sales']+=row.price
            first_visitb.loc[brand,'count']+=1
            firstdeptset.add(deptsdept)
            firstbrandset.add(brand)
        elif visit_count == 2:
            second_visit.loc[deptsdept,'sales']+=row.price
            second_visit.loc[deptsdept,'count']+=1
            second_visitb.loc[brand,'sales']+=row.price
            second_visitb.loc[brand,'count']+=1
            for dept1 in firstdeptset:
                price_table.loc[dept1,deptsdept]+=row.price
                count_table.loc[dept1,deptsdept]+=1
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
    for dept in deptsdepttuple:
        price_table.loc[dept,'0'] = sum(price_table.loc[dept,:])
        count_table.loc[dept,'0'] = sum(count_table.loc[dept,:])
        price_table.loc[dept,'-1'] = first_visit.loc[dept,'sales']
        count_table.loc[dept, '-1'] = first_visit.loc[dept, 'count']
    for dept in deptsdepttuple:
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

    price_table = price_table.rename(columns=strdeptdic,index=strdeptdic,level=0)
    count_table = count_table.rename(columns=strdeptdic,index=strdeptdic,level=0)
    brand_ptable = brand_ptable.rename(columns=zerodic,index=zerodic)
    brand_ctable = brand_ctable.rename(columns=zerodic,index=zerodic)

    return(price_table,count_table,brand_ptable,brand_ctable)


if __name__=='__main__':
    def cnv_deptlabel(table):
        table.columns = [int(x) for x in table.columns]
        table.index = [int(x) for x in table.index]
        return(table)
    zerodic = {-1:'初回計',0:'２回目合計'}

    depdic = pd.read_pickle(depttablefile)
    depdic.update(zerodic)
    sdeptdic = pd.read_pickle(sdepttablefile)

    strdeptdic = {}
    for k,v in depdic.items():
        dicfig = str(k).zfill(2)
        strdeptdic.update({dicfig:v})

    postable = pd.read_pickle(posfile)
    postable = postable.reset_index()
    user = pd.read_pickle(userfile)
    user = user.reset_index()
    user.registered_date = [datetime.strptime(x,'%Y%m%d') for x in user.registered_date]


    begindate = pd.Timestamp(2018,12,1)
    enddate =  pd.Timestamp(2019,12,31)
    postable = postable[postable.purchase_date >= begindate]
    postable = postable[postable.purchase_date <= enddate]
    temp_pos_target = top_users(postable,0.2)

    target_users = user[user.registered_date>=begindate]
    target_users = target_users[target_users.registered_date<=enddate]
    target_user_set = set(target_users.user_id)
    print ("registered user count = "+str(len(target_user_set)))
    pos_target = postable[postable.user_id.isin(target_user_set)]
    ret1,ret2,ret3,ret4 = set_freq(pos_target,sdeptdic,strdeptdic,zerodic)

    ret1.to_excel(outpath+'price15.xlsx')
    ret2.to_excel(outpath+'count15.xlsx')
    ret3.to_excel(outpath+'brandprice15.xlsx')
    ret4.to_excel(outpath+'brandcount15.xlsx')

    new_pos_target = top_users(pos_target,0.2)

    ret1,ret2,ret3,ret4 = set_freq(new_pos_target,sdeptdic,strdeptdic,zerodic)

    ret1.to_excel(outpath+'price15tp.xlsx')
    ret2.to_excel(outpath+'count15tp.xlsx')
    ret3.to_excel(outpath+'brandprice15tp.xlsx')
    ret4.to_excel(outpath+'brandcount15tp.xlsx')


    pos_target2 = postable
    rest_users = set(pos_target2.user_id) - target_user_set
    print ("registered user count = "+str(len(rest_users)))

    pos_target2 = pos_target2[pos_target2.user_id.isin(rest_users)]

    ret1, ret2, ret3, ret4 = set_freq(pos_target2,sdeptdic,strdeptdic,zerodic)
    ret1.to_excel(outpath + 'price25.xlsx')
    ret2.to_excel(outpath + 'count25.xlsx')
    ret3.to_excel(outpath + 'brandprice25.xlsx')
    ret4.to_excel(outpath + 'brandcount25.xlsx')

    new_pos_target2 = top_users(pos_target2,0.2)

    ret1,ret2,ret3,ret4 = set_freq(new_pos_target2,sdeptdic,strdeptdic,zerodic)

    ret1.to_excel(outpath + 'price25tp.xlsx')
    ret2.to_excel(outpath + 'count25tp.xlsx')
    ret3.to_excel(outpath + 'brandprice25tp.xlsx')
    ret4.to_excel(outpath + 'brandcount25tp.xlsx')

