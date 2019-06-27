import matplotlib.pyplot as plt
import pandas as pd
import datetime
import numpy
from mpl_toolkits.mplot3d.axes3d import Axes3D
from posenv import posfile,depttablefile,deptsdepttablefile,userfile,itemvecfile
if __name__ == "__main__":
    postable = pd.read_pickle(posfile)
    depdic = pd.read_pickle(depttablefile)
    d_sdeptdic = pd.read_pickle(deptsdepttablefile)
    user = pd.read_pickle(userfile)
    itemvecall = pd.read_pickle(itemvecfile)
    
    shoe_pos = postable[postable.DEPT==1]
#    shoe_pos = postable[postable.DEPT==11]
    '''
    shoe_pos = shoe_pos[shoe_pos.purchase_date>datetime.date(2017,1,1)]
    shoe_pos = shoe_pos[shoe_pos.purchase_date<datetime.date(2017,12,31)]
    '''

    ref_pos = postable[postable.purchase_date>datetime.date(2017,7,1)]
    ref_pos = ref_pos[ref_pos.purchase_date<datetime.date(2017,7,30)]
    user1 = ref_pos.user_id

    ref_pos = postable[postable.purchase_date>datetime.date(2017,1,1)]
    ref_pos = ref_pos[ref_pos.purchase_date<datetime.date(2017,1,30)]
    user2 = ref_pos.user_id


    ref_pos = postable[postable.purchase_date>datetime.date(2017,4,1)]
    ref_pos = ref_pos[ref_pos.purchase_date<datetime.date(2017,4,30)]
    user3 = ref_pos.user_id
    mut12 = set(user1) & set(user2)
    mut13 = set(user1) & set(user3)
    mut23 = set(user2) & set(user3)

    checkusers = mut12 | mut13 | mut23
#    ref_pos = ref_pos[['user_id','price']]
#    sum_sales = ref_pos.groupby('user_id').sum()
#    sum_sales = sum_sales[sum_sales.price>50000]

#    women = user[user.gender=='女性']
#    shoe_pos = shoe_pos[shoe_pos.user_id.isin(women.index)]
    shoe_pos = shoe_pos[shoe_pos.user_id.isin(checkusers)]


#    women = user[user.gender=='女性']
#    shoe_pos = shoe_pos[shoe_pos.user_id.isin(women.index)]

    sdlist = [1]
#    ,2,3,4,5,6,7,8,9,10,11]
#    sdlist = [2]

    for sd in sdlist:
        sd_pos = shoe_pos[shoe_pos.SDEPT==sd]
        mean_prices = pd.pivot_table(sd_pos,index='year_week',columns='jan_code',values='unit_price',aggfunc='mean').fillna(0)
        cost_prices = pd.pivot_table(sd_pos,index='year_week',columns='jan_code',values='cost',aggfunc='max')
        sum_prices = pd.pivot_table(sd_pos,index='year_week',columns='jan_code',values='price',aggfunc='sum').fillna(0)
        item_share = pd.DataFrame(0,index=sum_prices.index,columns=sum_prices.columns)
        for ind in item_share.index:
            total = sum(sum_prices.loc[ind,:])
            item_share.loc[ind,:] = sum_prices.loc[ind,:]/total
        item_sum = pd.DataFrame(0,index=sum_prices.columns,columns=['sum'])
        for col in item_share.columns:
            total = sum(sum_prices.loc[:,col])
            item_sum.loc[col,'sum'] = total
        item_sum = item_sum.sort_values(by=['sum'],ascending = False)
        itemvec = itemvecall[itemvecall.index.isin(item_sum.index)]
        for col in item_sum.index[:5]:
            print (col)
            vec = itemvec.loc[col,:]
            metric = itemvec.dot(vec.T)
            metric = metric.sort_values(ascending = False)
            simitem = metric.index[1]
            print (simitem)
            m = mean_prices.loc[:,col]
            s = item_share.loc[:,col]
            sm = sum_prices.loc[:,col]

            '''
            ms = mean_prices.loc[:,simitem]
            ss = item_share.loc[:,simitem]
            sms = sum_prices.loc[:,simitem]
            priceratio = ms/m
            shareratio = s/ss
            plt.title(col+' vs '+simitem)
            plt.scatter(priceratio,shareratio)
            plt.show()
            '''

#            print (m)
#            print (s)
            listm=[]
            lists=[]
            listyw=[]
            for i in range(len(m)):
                if not(m[i] == 0):
                    listm.append(m[i])
                    lists.append(s[i])
                    listyw.append(mean_prices.index[i])
#            normm = numpy.linalg.norm(m)
#            norms = numpy.linalg.norm(s)
#            listm = listm/normm
#            lists = lists/norms

            fig, ax = plt.subplots(2, 1, figsize=(12, 8), constrained_layout=True)
            ax[0].set_title(col)

            ax[0].plot(listyw,listm)
#            plt.show()
            ax[1].set_title(col)
            ax[1].plot(listyw,lists)
            plt.show()
            cr = numpy.corrcoef(listm,lists)
            print ("corr of "+col+" is "+str(cr))
#            plt.scatter(m, sm)
#            plt.show()
        margin_ratio = pd.DataFrame(0,index=sum_prices.index,columns=sum_prices.columns)
        margin_ratio = (mean_prices-cost_prices)/mean_prices
