import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime
import os
import numba
import datetime as dt
import tableclass as tb
from sklearn.decomposition import NMF
from sklearn.preprocessing import normalize
from sklearn.neighbors import NearestNeighbors
from sklearn.cluster import KMeans
from sklearn.cluster import AgglomerativeClustering
from  scipy.spatial.distance  import pdist
from scipy.cluster.hierarchy import linkage, dendrogram
from numba import jit

filelist = [
u'1701DM/008閉店セールDM',
u'1701DM/030閉店セールDM',
u'1701DM/072_特別優待DM',
u'1701DM/251閉店セールDM',
u'1701DM/803閉店セールDM',
u'1701DM/玉川特販DM',

u'1702DM/156オープンDM',
u'1702DM/633決算セールDM',
u'1702DM/635決算セールDM',
u'1702DM/636セールなし',
u'1702DM/スプリングセールDM',

u'1704DM/634一周年セールDM',
u'1704DM/半期決算セールDM',
#1704DM/半期決算セールDM02

u'1705DM/夏山セールDM',
#u'1705DM/上得意向けDM/005',
#u'1705DM/上得意向けDM/009',
#u'1705DM/上得意向けDM/011',
#u'1705DM/上得意向けDM/020',
#u'1705DM/上得意向けDM/021',
#u'1705DM/上得意向けDM/022',
#u'1705DM/上得意向けDM/033',
#u'1705DM/上得意向けDM/035',
#u'1705DM/上得意向けDM/044',
#u'1705DM/上得意向けDM/048',
u'1705DM/上得意向けDM/上得意向けDM',
u'1706DM/天満屋岡山特販DM',
u'1706DM/FC夏山DM/632',
u'1706DM/FC夏山DM/634',
u'1706DM/FC夏山DM/636',
u'1706DM/閉店セールDM/016閉店セールDM',
u'1706DM/閉店セールDM/039閉店セールDM',
u'1706DM/閉店セールDM/152閉店セールDM',
u'1707DM/玉川サマーバーゲンDM',
u'1707DM/大阪OMM特販DM',
u'1707DM/緑井天満屋特販DM',
#u'1707DM/ノースフェイスDM/011ノースDM',
#u'1707DM/ノースフェイスDM/012ノースDM',
#u'1707DM/ノースフェイスDM/023ノースDM',
u'1707DM/ノースフェイスDM/ノースフェイスDM',
u'1707DM/閉店セールDM/028閉店セールDM',
u'1707DM/閉店セールDM/055閉店セールDM',
u'1707DM/閉店セールDM/078閉店セールDM',
u'1708DM/072_DM',
u'1708DM/オータムセールDM',
u'1708DM/028・055・078オープンセールDM/028オープンセールDM',
u'1708DM/028・055・078オープンセールDM/055オープンセールDM',
u'1708DM/028・055・078オープンセールDM/078オープンセールDM',
u'1709DM/29・43閉店セールDM',
u'1709DM/636一周年記念DM',
u'1709DM/決算セールDM',
#u'1710DM/GRなんば-BオープンDM',
u'1712DM/GFO特販DM'
]

def Core_outputratio(folder,file,pos,u_list):
    shop_user_sales = pos[pos.user_id.isin(u_list)]
    
    shop_user_month = shop_user_sales.groupby('month').sum()
#    shop_user_month = shop_user_month['price']
    shop_user_month = shop_user_month.rename(columns = {'price':'user_sales'})
    shop_total_month = pos.groupby('month').sum()
#    shop_total_month = shop_total_month['price']
    shop_total_month = shop_total_month.rename(columns = {'price':'total_sales'})
    shop_total_month.loc[:,'user_sales'] = shop_user_month.loc[:,'user_sales']
    shop_total_month.loc[:,'user_sales_ratio'] = shop_total_month.loc[:,'user_sales']/shop_total_month.loc[:,'total_sales']
    shop_total_month = shop_total_month[['total_sales','user_sales','user_sales_ratio']]
    std = np.std(shop_total_month.user_sales_ratio)
    mean = np.mean(shop_total_month.user_sales_ratio)
    shop_total_month.loc[:,'std_value'] = 10*((shop_total_month.loc[:,'user_sales_ratio'] - mean)/std)+50
    
    list_length = len(u_list)
    for m in range(12):
        mn = m+1
        thismonthsales = shop_user_sales[shop_user_sales.month==mn]
        c_count = len(set(thismonthsales.user_id))
        shop_total_month.loc[mn,'active_ratio'] = c_count/float(list_length)
    

    shop_total_month.to_csv(tb.filepos+folder+file+'.csv')

table_dic = {u'入会店舗':'shop',u'会員番号':'user_id'}
def OutputRatio(folder,file,pos):
    tablefile = tb.fileinputpos+folder+file+'.xlsx'
    df = pd.read_excel(tablefile)
    df = df.rename(columns = table_dic)
    print ("target file is "+file)
    
    if ('shop' in df.columns):
        shopsales = pos[pos.shop.isin(df.shop)]
    else:
        shopsales = pos
    df.loc[:, 'user_id'] = list(map((lambda x: str(x)), df.user_id))
    Core_outputratio(folder,file,shopsales,df.user_id)


if __name__ == '__main__':
    folder = u'yamaguchi_GM/'
    usertablefile = 'cleanutable'
    ut = tb.UserTable(usertablefile)
    usertable = ut.usertable

    
    tabdic = {}
    DMproperty = pd.DataFrame(0,index = filelist,columns = ['average_age','min_age','max_age','min_regdate','max_regdate'])
    for filn in filelist:
        tablefile = tb.fileinputpos+folder+filn+'.xlsx'
        df = pd.read_excel(tablefile)
        df = df.rename(columns = table_dic)
        df.loc[:, 'user_id'] = list(map((lambda x: str(x)), df.user_id))
        tabdic.update({filn:df})
        print("target file is " + tablefile)

        DMusers = usertable[usertable.index.isin(df.user_id)]
        DMproperty.loc[filn,'average_age'] = np.mean(DMusers.age)
        DMproperty.loc[filn,'min_age'] = np.min(DMusers.age)
        DMproperty.loc[filn,'max_age'] = np.max(DMusers.age)
        DMproperty.loc[filn,'min_regdate'] = np.min(DMusers.registered_date)
        regset = set(DMusers.registered_date)
        maxval = max(regset)
        while  maxval.year > 2017:
            regset.remove(maxval)
            maxval = max(regset)
        DMproperty.loc[filn,'max_regdate'] = maxval
    
    DMproperty.to_csv(tb.filepos+folder+'DMproperty.csv')
    
    counttable = pd.DataFrame(0,index = filelist,columns=filelist)
    fillen = len(filelist)
    for i in range(fillen):
        ind = filelist[i]
        ind_t = tabdic.get(ind)
        ind_t_len = len(ind_t.user_id)
        ind_set = set(ind_t.user_id)
        for j in range(fillen):
            col = filelist[j]
            col_t = tabdic.get(col)
            overlap = ind_set & set(col_t.user_id)
            overlap_count = len(overlap)
            ovelap_ratio = overlap_count/float(ind_t_len)
            counttable.loc[ind,col] = ovelap_ratio
#            counttable.loc[col, ind] = ovelap_ratio
    counttable.to_csv(tb.filepos+folder+'DMovelapcount.csv')
    
    
    depttable = tb.DEPTtable('HITRMD_DEPT')

    pos16= tb.postable(tb.posnamelist[5])
    pos17= tb.postable(tb.posnamelist[6])
    pos16 = pos16.table
    pos17 = pos17.table
    pos17.loc[:,'month'] = list(map((lambda x:x.month),pos17.purchase_date))
    pos17.loc[:,'itemid'] = list(map((lambda x,y: depttable.namedic[x]+depttable.subdic[x][y]),pos17.DEPT,pos17.SDEPT))
#    pos17.loc[:,'itemid'] = list(map((lambda x,y,z: depttable.namedic[x]+depttable.subdic[x][y]+z),pos17.DEPT,pos17.SDEPT,pos17.brand))
    pos16.loc[:,'month'] = list(map((lambda x:x.month),pos16.purchase_date))
    pos16.loc[:,'itemid'] = list(map((lambda x,y,z: depttable.namedic[x]+depttable.subdic[x][y]+z),pos16.DEPT,pos16.SDEPT,pos16.brand))
    for filname in filelist:
        OutputRatio(folder,filname,pos17)

    janusales = pos16[pos16.month==1]
    janu_purchasers = set(janusales.user_id)
    aprilsales = pos16[pos16.month==4]
    april_purchasers = set(aprilsales.user_id)
    julysales = pos16[pos16.month==7]
    july_purchasers = set(julysales.user_id)
    sales_lovers = (july_purchasers & april_purchasers) & janu_purchasers
    sales_lovers = list(sales_lovers)
    
    Core_outputratio(folder,'sales_lovers',pos17,sales_lovers)

    janusales = pos17[pos17.month==4]
    janu_purchasers = set(janusales.user_id)
    aprilsales = pos17[pos17.month==5]
    april_purchasers = set(aprilsales.user_id)
    julysales = pos17[pos17.month==6]
    july_purchasers = set(julysales.user_id)
    sales_lovers = (july_purchasers | april_purchasers) | janu_purchasers
    sales_lovers = list(sales_lovers)
    
    Core_outputratio(folder,'premonthbuyers',pos17,sales_lovers)

    julysales = pos16[pos16.month==7]
    july_purchasers = set(julysales.user_id)
    sales_lovers = list(july_purchasers)
    
    Core_outputratio(folder,'summer_lovers',pos17,sales_lovers)

    julysales = pos16[pos16.month==7]
    julysales = julysales[julysales.DEPT == 26]
    campsales = pos17[pos17.DEPT == 26]

    camp_purchasers = set(julysales.user_id)
    sales_lovers = list(camp_purchasers)
    
    Core_outputratio(folder,'camp_lovers',campsales,camp_purchasers)

    print("pivot table conversion start")
    userbyitem = pd.pivot_table(pos17,index='user_id',columns= 'itemid',values='price',aggfunc='count').fillna(0)
#    userbyitem = pd.pivot_table(pos17,index='user_id',columns= 'itemid',values='price',aggfunc='sum').fillna(0)
#    userbyitem[userbyitem<0] = 0
#    userbyitem= userbyitem.loc[(userbyitem != 0).any(axis=1)]
    print("pivot table conversion end")
    print ("matrix factorization start")
    model = NMF(n_components = 10,init='random',random_state=0)
    P = model.fit_transform(userbyitem)
    Q = model.components_
    print ("matrix factorization complete")
    
    user_vec=pd.DataFrame(P,index=userbyitem.index)
    item_vec = pd.DataFrame(Q.T,index = userbyitem.columns)
    print ("item clustering caluculation start")

    nn = AgglomerativeClustering(n_clusters = 20,affinity  = 'cosine',linkage ='complete')
    nn.labels_ = item_vec.index
    labels = nn.fit_predict(item_vec)
    print ("clustering caluculation complete")
    labels_item = pd.DataFrame(labels,index = item_vec.index,columns=['cluster'])
    labels_item = labels_item.sort_values(by=['cluster'])
    labels_item.to_csv( tb.filepos+'labels.csv')
    print ("labels = "+str(labels))
    
    norm_u_vec = normalize(user_vec,axis = 1)
    print ("user clustering caluculation start")
    kmeans = KMeans(n_clusters = 10,random_state=0).fit(norm_u_vec)
    kmeans.labels_ = user_vec.index
    labels = kmeans.fit_predict(user_vec)
    print ("clustering caluculation complete")
    labels = pd.DataFrame(labels,index = user_vec.index,columns=['cluster'])
    labels = labels.sort_values(by=['cluster'])
    labels.to_csv( tb.filepos+'usercluster.csv')
    pos17.loc[:,'cluster'] = list(map((lambda x: labels_item.loc[x]),pos17.itemid))
    outtable = pd.DataFrame(0,index = [0,1,2,3,4,5,6,7,8,9],columns=['dummpy'])

    for cc in range(10):
        labelscc=labels[labels.cluster==cc]
        cluster0 = pos17[pos17.user_id.isin(labelscc.index)]
        cluster0 = cluster0[['price','cluster']]
        bycluster = cluster0.groupby('cluster').count()
#        bycluster = cluster0.groupby('cluster').sum()
        bycluster.rename(columns = {'price':cc},inplace = True)
        outtable = outtable.join(bycluster)
    outtable.to_csv(tb.filepos+'bycluster.csv')


