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
from numba import jit


from scipy.spatial import distance
from scipy.cluster import hierarchy

@jit
def pricerange(price):
    if price <500:
        return('500')
    elif price <1000:
        return('1000')
    elif price <3000:
        return('3000')
    elif price <5000:
        return('5000')
    elif price <10000:
        return('10000')
    elif price < 30000:
        return('30000')
    elif price <50000:
        return('50000')
    elif price <100000:
        return('100000')
    elif price < 150000:
        return('150000')
    elif price <200000:
        return('200000')
    elif price <300000:
        return('300000')
    elif price <500000:
        return('500000')
    else:
        return('1000000')

@jit
def sdeptstr(list1,list2,dic1,dic2):
    maxlen = len(list1)
    retlist = []
    for i in range(maxlen):
        d2 = dic2[list1[i]].get(list2[i],0)
        if d2 == 0:
            print ("error at i = ",str(i))
            print ("DEPT = "+str(list1[i]))
            print ("dept name = "+dic1[list1[i]])
            print ("SDEPT = "+str(list2[i]))
        else:
            s = dic1[list1[i]]+dic2[list1[i]][list2[i]]
            retlist.append(s)
    return(retlist)
class brandmetric(object):
    def __init__(self,postable,tb):
        self.prefix = 'count'
        filename = 'brandveccount.pkl'
        filename = tb.filepos+filename
        depttable = tb.DEPTtable('HITRMD_DEPT')
        if os.path.exists(filename):
            self.itemvec = pd.read_pickle(filename)
        else:
            print("pivot table conversion start")
            postable.loc[:,'month'] = list( map((lambda x: x.month), postable.purchase_date))
            postable.loc[:,'price_range'] = list(map(pricerange,postable.price))
            slist = list(map(lambda x, y: depttable.namedic[x]+depttable.subdic[x][y],postable.DEPT,postable.SDEPT))
#            slist = sdeptstr(postable.DEPT,postable.SDEPT, depttable.namedic,depttable.subdic)
            postable.loc[:,'NEWSDEPT'] = slist
            purchae_table = pd.pivot_table(postable,index = 'user_id',columns = 'brand',values = 'price',aggfunc = 'count').fillna(0)
            dept_table = pd.pivot_table(postable,index = 'user_id',columns = 'DEPT',values = 'price',aggfunc = 'count').fillna(0)
            dept_table = dept_table.rename(columns= depttable.namedic)
            sdept_table = pd.pivot_table(postable,index = 'user_id',columns = 'NEWSDEPT',values = 'price',aggfunc = 'count').fillna(0)
            month_table = pd.pivot_table(postable,index = 'user_id',columns = 'month',values = 'price',aggfunc = 'count').fillna(0)
            range_table = pd.pivot_table(postable,index = 'user_id',columns = 'price_range',values = 'price',aggfunc = 'count').fillna(0)
            print("col brand = "+str(purchae_table.columns))
            print("col dept = "+str(dept_table.columns))
            print("col sdept = "+str(sdept_table.columns))
            print("col month = "+str(month_table.columns))

            dept_table = dept_table.join(sdept_table,how ='left').fillna(0)
            dept_table = dept_table.join(month_table,how ='left').fillna(0)
            purchae_table = dept_table.join(purchae_table,how ='left').fillna(0)
            purchae_table = purchae_table.join(range_table,how ='left').fillna(0)

            print("pivot table conversion complete")
            model = NMF(n_components = 50, init='random',random_state = 0)
            P = model.fit_transform(purchae_table.values)
            Q = model.components_
            Q = normalize(Q.T)
            self.itemvec = pd.DataFrame(Q,index = purchae_table.columns)
            self.itemvec.to_pickle(filename)
    def SaveItemMetrics(self,brandname):
        vec = self.itemvec.loc[brandname,:].values

        values = np.matmul(vec,self.itemvec.values.T)
        metrics = pd.DataFrame(values,index = self.itemvec.index,columns = ['metric'])
        metrics = metrics.sort_values(by=['metric'],ascending = False)
        metrics.to_csv(tb.filepos+self.prefix+brandname+'.csv')
            

if __name__=='__main__':
    pos17= tb.postable(tb.posnamelist[6])
    table17= pos17.table
    purchae_sum = table17.groupby("user_id").sum()
    ut = tb.UserTable('cleanutable')
    utable = ut.usertable
#    utable = utable.set_index('user_id')
    table17 = table17.set_index('user_id')
    table17 = table17.join(utable,how = 'left',lsuffix='pos_',rsuffix='ut_')

    purchae_sum = purchae_sum.sort_values(by = ["price"],ascending = False)
    top10 = purchae_sum.index[0:10]
    for i in range(10):
        toptable = table17[table17.index == top10[i]]
#        toptable = toptable.drop("user_id",axis = 1)
        toptable.to_csv(tb.filepos+"top"+str(i)+".csv")
    

    posall = tb.postable('unified').table
    met = brandmetric(posall,tb)

    '''
    res = hierarchy.linkage(met.itemvec,metric='cosine')
    arr = hierarchy.fcluster(res,1.065)
    labels = pd.DataFrame(arr,index = met.itemvec.index,columns=['cluster'])
    labels = labels.sort_values(by=['cluster'])
    labels.to_csv( tb.filepos+'labels.csv')

    np.savetxt( tb.filepos+"temp.csv", res, delimiter=",")
    hierarchy.dendrogram(res,p=15,truncate_mode='lastp')
    plt.show()

    nn = NearestNeighbors(n_clusters = 4,metric = 'cosine',n_jobs = -1)
    nn.fit(met.itemvec)
    arr = nn.kneighbors(met.itemvec,return_distance = False)
    np.savetxt( tb.filepos+"temp.csv", arr, delimiter=",")
    print ("arr = "+str(arr))
    '''

    nn = AgglomerativeClustering(n_clusters = 30,affinity  = 'cosine',linkage ='complete')
    nn.labels_ = met.itemvec.index
    labels = nn.fit_predict(met.itemvec)
    labels = pd.DataFrame(labels,index = met.itemvec.index,columns=['cluster'])
    labels = labels.sort_values(by=['cluster'])
    labels.to_csv( tb.filepos+'labels.csv')
    print ("labels = "+str(labels))

    '''

    met.SaveItemMetrics(u'スノーピーク')
    met.SaveItemMetrics(u'伊藤園')
    met.SaveItemMetrics(u'ローバー')
    met.SaveItemMetrics(u'デサント')
    met.SaveItemMetrics(u'ノースフェイス')

    possnow = posall[posall.brand == u'スノーピーク']
    snowc = set(possnow.user_id)
    print ("count of snow customers = "+str(len(snowc)))
    posnorth = posall[posall.brand == u'ノースフェイス']
    northc = set(posnorth.user_id)
    print ("count of north customers = "+str(len(northc)))
    poscol = posall[posall.brand == u'コロンビア']
    colc = set(poscol.user_id)
    print("count of columbia customers = " + str(len(colc)))

    mut = snowc & northc
    print ("hight of snow north = "+str(len(mut)))

    mut = snowc & colc
    print ("hight of snow col = "+str(len(mut)))
    '''


    '''
    Matrix factorization 
    多量購入者　購入品目具体例
    ターゲットボリュームゾーン分析
    登山靴分析
        登山靴を二足以上買っている客
            インターバル
            店舗
            前回と次回の価格相関
            同じブランドかどうか
            
    '''
    

