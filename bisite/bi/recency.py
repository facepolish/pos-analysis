import pandas as pd
from .posenv import recencyfile
from  .dashboard import KojitsuPos
import datetime as dt

recency_intervals = [0, 30, 90, 180, 365, 730, 1095]
category = ['sales', 'ratio']
names = ['category', 'intervals']
cols = pd.MultiIndex.from_product([category, recency_intervals], names=names)

def get_stack(table):
    ratio = pd.DataFrame(0,index=table.index,columns = recency_intervals)
    sales = pd.DataFrame(0,index=table.index,columns = recency_intervals)
    ratio.loc[:,recency_intervals[0]] = table.loc[:,('ratio',recency_intervals[0])]
    sales.loc[:,recency_intervals[0]] = table.loc[:,('sales',recency_intervals[0])]
    for i in range(1,len(recency_intervals)):
        ratio.loc[:,recency_intervals[i]] = table.loc[:,('ratio',recency_intervals[i])] + ratio.loc[:,recency_intervals[i-1]]
        sales.loc[:,recency_intervals[i]] = table.loc[:,('sales',recency_intervals[i])] + sales.loc[:,recency_intervals[i-1]]
    return(sales,ratio)

def PosQueryRecency(term,shop):
    idx = pd.IndexSlice
    kp = KojitsuPos()
    table = kp.postable
    if not(shop==0):
        table = table[table.shop==shop]
    targetpos = table[table.purchase_date>=term[0]]
    targetpos = targetpos[targetpos.purchase_date<=term[1]]
    weeklist = set(targetpos.year_week)

    res_table = pd.DataFrame(0,index = weeklist,columns=cols)

    for this_week in weeklist:
        this_week_table = table[table.year_week == this_week]
        this_week_min = min(this_week_table.purchase_date)
        this_week_max = max(this_week_table.purchase_date)
        outf = recency_calc(table,this_week_min,this_week_max,this_week)
        res_table.loc[this_week,:] = outf.loc[this_week,:]
    res_table = res_table.sort_index()
    dates = [ dt.datetime.strptime(d+'-1','%Y %W-%w').strftime('%Y-%m-%d') for d in res_table.index]
    res_table.loc[:,'date'] = dates

    return(res_table)


    
def recency_calc(table,beg_date,end_date,index_label):
    len_intervals = len(recency_intervals)
    out_frame = pd.DataFrame(0,index=[index_label],columns = cols)

    targetterm = table[table.purchase_date<end_date]
    targetterm = targetterm[targetterm.purchase_date>=beg_date]
    oldterm = table[table.purchase_date<beg_date]
    oldterm = oldterm[['user_id','purchase_date']]
    groupset = {}
    terms = {}
    sales = {}
    for i in range(len_intervals):
        terms.update({i:beg_date-dt.timedelta(days=recency_intervals[i])})
    purchased_users = set(targetterm.user_id)
    
    oldterm = oldterm[oldterm.user_id.isin(purchased_users)]
    
    userrecency = oldterm.groupby('user_id').agg({'purchase_date':max})

    groupset.update({0:purchased_users - set(oldterm.user_id)})
        
    group1 = userrecency[userrecency.purchase_date>terms[1]]
    groupset.update({1:set(group1.index)})
    for i in range(2,len_intervals):
        group = userrecency[userrecency.purchase_date<=terms[i-1]]
        group = group[group.purchase_date>terms[i]]
        groupset.update({i:set(group.index)})

    group = userrecency[userrecency.purchase_date<=terms[6]]
    groupset.update({7:set(group.index)})

    totalsales = sum(targetterm.price)

    print ("latest date is "+str(index_label))
    print ("begining of target date is "+str(beg_date))
    for i in range(len_intervals):
        term_sales = targetterm[targetterm.user_id.isin(groupset[i])]
        sales.update({i:sum(term_sales.price)}) 
        out_frame.loc[index_label,('ratio',recency_intervals[i])] = sales[i]/totalsales
        out_frame.loc[index_label, ('sales',recency_intervals[i])] = sales[i]
    return(out_frame)

def create_year_week_table(table,intervals,lastresult=None):
    max_week = max(table.year_week)
    tablelastday = min(table.purchase_date)+dt.timedelta(days=intervals[len(intervals)-1])
    temp_table = table[table.purchase_date>tablelastday]
    last_week = min(temp_table.year_week)
    weeklist = set(temp_table.year_week) - set([max_week,last_week])
    if not(lastresult == None):
        pre_exist_weeks = set(lastresult.index)
        weeklist = weeklist - pre_exist_weeks

    cache_table_ratio = pd.DataFrame(0,index = weeklist,columns = intervals)
    cache_table_sales = pd.DataFrame(0,index = weeklist,columns = intervals)

    for this_week in weeklist:
        this_week_table = table[table.year_week == this_week]
        this_week_min = min(this_week_table.purchase_date)
        this_week_max = max(this_week_table.purchase_date)
        sales,ratio = recency_calc(table,this_week_min,this_week_max,intervals,this_week)
        cache_table_ratio.loc[this_week,:] = ratio.loc[this_week,:]
        cache_table_sales.loc[this_week,:] = sales.loc[this_week,:]
            
    return(cache_table_sales,cache_table_ratio)
'''
class recency(KojitsuPos):
    def convert_sales_to_ratio(sales):
        ratio = pd.DataFrame(0,index = sales.index,columns = sales.columns)
        for ind,row in sales.iterrows():
            total = sum(row.loc[ind,:])
            ratio.loc[ind,:] = sales.loc[ind,:]/total
    postable = super().GetPosTable()
    if os.path.exists(recencyfile):
        recency_sales = pd.read_pickle(recencyfile)
        recency_sales_extra,recency_ratio = create_year_week_table(postable,recency_intervals,recency_sales)
        recency_sales = recency_sales_extra.append(recency_sales)
        recency_sales.to_pickle(recencyfile)
        recency_ratio = convert_sales_to_ratio(recency_sales)
    else:
        recency_sales,recency_ratio = create_year_week_table(postable,recency_intervals)
    def __init__(self):
        
'''
