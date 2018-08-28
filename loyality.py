import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime
import os
import numba
import datetime as dt
import tableclass as tb

@numba.jit
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
def draw_hist (table,lower,upper = 0):
    drawtable = table[table.price >=lower]
    if upper != 0:
        drawtable = drawtable[drawtable.price < upper]
    plt.hist(drawtable.purchase_date,bins=100)
    plt.show()
def high_all_ratio (table):
    allsum = table.price.sum()
    table.loc[:,'all_ratio'] = table.price / (float(allsum))
    highsum = table.high.sum()
    table.loc[:,'high_ratio'] = table.high / (float(highsum))
    table.loc[:,'high/all'] = table.high_ratio / table.all_ratio
    table = table.sort_values(by=['high/all'], ascending=False)
    return(table)


if __name__ == '__main__':
    cols = ['user_id','purchase_date','price']
    salesbyuserfile = tb.filepos+'SaleByYear1516'
    birth_file = tb.filepos+'birthsale'
    amount_count_file = tb.filepos+'amount_count'
    pos15= tb.postable(tb.posnamelist[4])
    table15= pos15.table
    pos16= tb.postable(tb.posnamelist[5])
    table16= pos16.table
    pos17= tb.postable(tb.posnamelist[6])
    table17= pos17.table
    web15 = tb.websalestable(2015)
    web16 = tb.websalestable(2016)
    web17 = tb.websalestable(2017)
    web15 = web15.table
    web16 = web16.table
    web17 = web17.table
    table15 = table15.loc[:,cols]
    table16 = table16.loc[:,cols]
    table15 = table15.append(web15)
    table16 = table16.append(web16)
    table1617 = table16.append(table17)
    table1617 = table1617.append(web17)


#    tb.UserTable()
    birth_table = tb.birthtable().table
    birth_table = birth_table.drop_duplicates(subset = 'user_id')

    years = ['sales2015','sales2016']
    userlist = set(table15.user_id) | set(table16.user_id)
    userlist = list(userlist)
    
    userlist2 = set(table16.user_id) & set(birth_table.user_id)
    table_for_b = table16[table16.user_id.isin(userlist2)]

    table_for_b = table_for_b.sort_values(by = 'user_id')
    table_for_b = table_for_b.set_index('user_id')
    
    userlist2 = list(userlist2)

    u_table = pd.DataFrame(0,index = userlist,columns=years)
    b_sales = pd.DataFrame(0,index = userlist2,columns=['total',"bmonth"])
    birth_table = birth_table.set_index('user_id')

    print("group by operation start")
    table15sum = table15.groupby('user_id').sum()
    table16sum = table16.groupby('user_id').sum()


    plt.hist(table15sum.price,bins=100,range =(0,100000))
    plt.show()
    plt.hist(table16sum.price,bins=100,range =(0,100000))
    plt.show()
    rokugou = table15sum[(table15sum.price>=100000)]



    rokugou = rokugou[(rokugou.price < 300000)]
    rokugou = table16sum[table16sum.index.isin(rokugou.index)]
    plt.hist(rokugou.price,bins=100,range =(0,400000))
    plt.show()
    plt.hist(rokugou.price,bins=20,range =(90000,110000))
    plt.show()
    count_of_rokugou = rokugou.shape[0]
    cont_roku = rokugou[rokugou.price>=100000]
    cont_coun_roku = cont_roku.shape[0]
    print("rokugou cont ratio = "+str(float(cont_coun_roku)/float(count_of_rokugou)))

    nanagou = table15sum[(table15sum.price>=300000)]
    nanagou = nanagou[(nanagou.price < 500000)]
    nanagou = table16sum[table16sum.index.isin(nanagou.index)]
    plt.hist(nanagou.price,bins=100,range =(0,600000))
    plt.show()
    count_of_nanagou = nanagou.shape[0]
    cont_nana = nanagou[nanagou.price>=300000]
    cont_coun_nana = cont_nana.shape[0]
    print("nanagou cont ratio = "+str(float(cont_coun_nana)/float(count_of_nanagou)))

    hachigou = table15sum[table15sum.price>=500000]
    hachigou = table16sum[table16sum.index.isin(hachigou.index)]
    
    plt.hist(hachigou.price,bins=100,range =(0,1000000))
    plt.show()
    count_of_hachi = hachigou.shape[0]
    cont_hachi = hachigou[hachigou.price>=500000]
    cont_coun_hachi = cont_hachi.shape[0]
    print("hahcigou cont ratio = "+str(float(cont_coun_hachi)/float(count_of_hachi)))
    begin_date = dt.date(2016,12,1)
    end_date = dt.date(2017,11,30)
    target1617 = table1617[table1617.purchase_date >= begin_date]
    target1617 = target1617[target1617.purchase_date <= end_date]
    target1617 = target1617.sort_values(by = ['user_id','purchase_date'])
    userlist3 = list(set(target1617.user_id))

    agg_table = pd.DataFrame(0,index = userlist3,columns = ['amount','count'])

#    target1617 = target1617.set_index(['user_id','purchase_date'])
    targetprice = target1617.loc[:,['user_id','price']]
    targetcount = target1617.loc[:,['user_id','purchase_date']]
    price_agg = targetprice.groupby('user_id').sum()
    count_agg = targetcount.groupby('user_id').agg(count_days)
    unified_table = price_agg.join(count_agg)
    draw_hist(unified_table,0,50000)
    draw_hist(unified_table,50000,100000)
    draw_hist(unified_table,100000,200000)
    draw_hist(unified_table,200000,300000)
    draw_hist(unified_table,300000,400000)
    draw_hist(unified_table,400000,500000)
    draw_hist(unified_table,500000,1000000)
    draw_hist(unified_table,1000000,2000000)
    draw_hist(unified_table,2000000,3000000)
    draw_hist(unified_table,3000000)

    high_purchasers = unified_table[unified_table.price>=300000]

    outcols = ['price']
    brandsum = table17.groupby('brand').sum()
    brandsum = brandsum.loc[:,outcols]
    deptsum = table17.groupby('DEPT').sum()
    deptsum = deptsum.loc[:,outcols]
    deptsum.to_csv(tb.filepos+'deptdall.csv')

    high17 = table17[table17.user_id.isin(high_purchasers.index)]

    brandsumhigh = high17.groupby('brand').sum()
    brandhigh = brandsumhigh.loc[:,outcols]
    brandhigh.rename(columns = {'price':'high'},inplace=True)
    brandsum = brandsum.join(brandhigh,how='outer')
    brandsum = high_all_ratio(brandsum)
    brandsum.to_csv(tb.filepos+'brandhigh.csv')

    depttable = tb.DEPTtable('HITRMD_DEPT')
    deptsumhigh = high17.groupby('DEPT').sum()
    deptsumhigh = deptsumhigh.loc[:,outcols]
    deptsumhigh.rename(columns = {'price':'high'},inplace=True)
    deptsum = deptsum.join(deptsumhigh,how='outer')

    deptsum = high_all_ratio(deptsum)
    deptsum.rename(index = depttable.namedic,inplace=True)
    deptsum.to_csv(tb.filepos+'deptdhigh.csv')



    if os.path.exists(birth_file):
        b_sales = pd.read_pickle(birth_file)
    else:
        user = 0
        maxcount = table_for_b.shape[0]
        print ("maxcount = "+str(maxcount))
        for usr,row in table_for_b.iterrows():
            b_sales.loc[usr,'total']+=row.price
            if user != usr:
                user = usr
                birthmonth = birth_table.loc[user,'birth_date']
                birthmonth = birthmonth.month
            if row.purchase_date.month == birthmonth:
                b_sales.loc[usr,'bmonth']+=row.price
        b_sales.to_pickle(birth_file)



    b_sales = b_sales[b_sales.index.isin(rokugou.index)]
    total_sales = sum(b_sales.total)
    total_bmonth = sum(b_sales.bmonth)
    print("sales of the month of birthday ratio = "+str(float(total_bmonth)/float(total_sales)))

    