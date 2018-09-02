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

class brandmetric(object):
    def __init__(self,postable,tb,payflag = False):
        if payflag == True:
            filename = 'brandveccpay.pkl'
            self.prefix = 'pay'
        else:
            self.prefix = 'count'
            filename = 'brandveccount.pkl'
        filename = tb.filepos+filename
        if os.path.exists(filename):
            self.itemvec = pd.read_pickle(filename)
        else:
            print("pivot table conversion start")
            if payflag == True:
                purchae_table = pd.pivot_table(postable,index = 'user_id',columns = 'brand',values = 'price',aggfunc = np.nansum).fillna(0)
            else:
                purchae_table = pd.pivot_table(postable,index = 'user_id',columns = 'brand',values = 'price',aggfunc = 'count').fillna(0)

            purchae_table = purchae_table.abs()
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
    met.SaveItemMetrics(u'スノーピーク')
    met.SaveItemMetrics(u'伊藤園')
    met.SaveItemMetrics(u'ローバー')
    met.SaveItemMetrics(u'デサント')
    met.SaveItemMetrics(u'ノースフェイス')

    met2 = brandmetric(posall,tb,payflag = True)
    met2.SaveItemMetrics(u'スノーピーク')
    met2.SaveItemMetrics(u'伊藤園')
    met2.SaveItemMetrics(u'ローバー')
    met2.SaveItemMetrics(u'デサント')
    met2.SaveItemMetrics(u'ノースフェイス')

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
    

