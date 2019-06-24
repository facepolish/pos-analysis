import matplotlib.pyplot as plt
import pandas as pd
from datetime import timedelta,datetime,date
from bi import recency,posenv


def recency_table(postable,title):
    latestdate = max(postable.purchase_date)
    begdate = latestdate-timedelta(days=30)
    label = str(begdate)+'から'+str(latestdate)+'まで'
    term = (pd.Timestamp(2017,11,1),pd.Timestamp(2017,11,30))
    table = recency.PosQueryRecency(term,0)
    table = recency.PosQueryRecency(term,0)

#    cat_sales,ratios = create_year_week_table(postable,datediff)
    sales,ratio = recency.get_stack(table)
    colors = ['tab:blue','tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
    fig,ax = plt.subplots( 2, 1, figsize=(12,8), constrained_layout=True)
    ax[0].set_xticklabels(table.date,rotation='vertical',fontsize = 'small')
    ax[1].set_xticklabels(table.date,rotation='vertical',fontsize = 'small')
    ax[0].fill_between(table.date,0,ratio.loc[:,recency.recency_intervals[0]],color=colors[0],label='sample')
    ax[1].fill_between(table.date,0,sales.loc[:,recency.recency_intervals[0]],color=colors[0],label='sample')
    for i in range(1,len(recency.recency_intervals)):
        ax[0].fill_between(table.date,ratio.loc[:,recency.recency_intervals[i-1]],ratio.loc[:,recency.recency_intervals[i]],color=colors[i])
        ax[1].fill_between(table.date,sales.loc[:,recency.recency_intervals[i-1]],sales.loc[:,recency.recency_intervals[i]],color=colors[i])
    plt.show()


    
if __name__=='__main__':

    postable = pd.read_pickle(posenv.posfile)
    recency_table(postable,' all ')
