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



if __name__ == '__main__':
    folder = u'yamaguchi_GM/'
    usertablefile = 'cleanutable'
    ut = tb.UserTable(usertablefile)
    usertable = ut.usertable
    
    depttable = tb.DEPTtable('HITRMD_DEPT')

    pos17= tb.postable(tb.posnamelist[6])
    pos17 = pos17.table
    pos16= tb.postable(tb.posnamelist[5])
    pos16 = pos16.table

    brandbuyers = pos17[pos17.brand == 'ノースフェイス']
    brandbuyers = set(brandbuyers.user_id)
    print("pivot table conversion start")
    userbyitem = pd.pivot_table(pos17,index='user_id',columns= 'brand',values='price',aggfunc='count').fillna(0)
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
    user_vec.to_pickle('C:/Users\Hiroshi Sakai/workspace/Kojitsu/src/cgi-bin/user.pkl')
    item_vec.to_pickle('C:/Users\Hiroshi Sakai/workspace/Kojitsu/src/cgi-bin/brand.pkl')
#    user_vec = user_vec[~user_vec.index.isin(brandbuyers)]
    print ("item clustering caluculation start")
    '''
    user_metric = user_vec.dot(item_vec.loc['ノースフェイス',:].T)
    user_metric = user_metric.sort_values(ascending=False)
    top100 = user_metric.index[0:100]
    north_lovers = pos17[pos17.user_id.isin(top100)]
    north_lovers = north_lovers[['user_id','brand','price']]
    all17 = pos17[['brand','price']]
    
    north_lovers_count = north_lovers.groupby('brand').count()
    all_count = all17.groupby('brand').count()
    north_lovers_count.to_csv(tb.filepos+'north_lovers.csv')
    all_count.to_csv(tb.filepos+'all17.csv')
    user_metric.to_csv(tb.filepos+'northlover.csv')
    '''
