import matplotlib.pyplot as plt
import pandas as pd
from posenv import posfile
#from  dashboard import KojitsuPos
from datetime import timedelta,datetime,date
from recency import PosQueryRecency,get_stack


def recency_table(postable,title):
    latestdate = max(postable.purchase_date)
    begdate = latestdate-timedelta(days=30)
    label = str(begdate)+'から'+str(latestdate)+'まで'
    term = (pd.Timestamp(2017,11,1),pd.Timestamp(2017,12,31))
    table = PosQueryRecency(term,0)

#    cat_sales,ratios = create_year_week_table(postable,datediff)
    sales,ratio = get_stack(table)
    colors = ['tab:blue','tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
    fig,ax = plt.subplots( 2, 1, figsize=(12,8), constrained_layout=True)
    ax[0].set_xticklabels(table.date,rotation='vertical',fontsize = 'small')
    ax[1].set_xticklabels(table.date,rotation='vertical',fontsize = 'small')
    ax[0].fill_between(table.date,0,ratio.loc[:,datediff[0]],color=colors[0],label='sample')
    ax[1].fill_between(table.date,0,sales.loc[:,datediff[0]],color=colors[0],label='sample')
    for i in range(1,len(datediff)):
        ax[0].fill_between(table.date,ratio.loc[:,datediff[i-1]],ratio.loc[:,datediff[i]],color=colors[i])
        ax[1].fill_between(table.date,sales.loc[:,datediff[i-1]],sales.loc[:,datediff[i]],color=colors[i])
    plt.show()


    
if __name__=='__main__':

    postable = pd.read_pickle(posfile)
#    recency_table(postable,' all ')

    shoptable = postable.groupby('shop').agg({'price':sum})
    shoptable = shoptable.sort_values(by='price',ascending=False)
    shoplist = shoptable.index[0:10]
    for shop in shoplist:
        posshop = postable[postable.shop == shop]
        print ("recency for shop "+str(shop))
        recency_table(posshop,str(shop))

    
    brandtable = postable.groupby('brand').agg({'price':sum})
    brandtable = brandtable.sort_values(by='price',ascending=False)
    brandlist = brandtable.index[0:10]
    for brand in brandlist:
        posbrand = postable[postable.brand == brand]
        print ("recency for brand "+brand)
        recency_table(posbrand,brand)


