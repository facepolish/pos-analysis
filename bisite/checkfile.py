import numpy as np
import pandas as pd
from bi.posenv import postempfile,itemdbfile,postempfile2,posfile
from bi.tableclass import posaddcols,convert_table
from pandas.api.types import CategoricalDtype
from scipy.sparse import csr_matrix,lil_matrix,dok_matrix
from math import sqrt
from bi.createitemvec import PivotAndNMF,PivotAndNMF_fixedU
from sklearn import preprocessing  # to normalise existing X
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import datetime as dt

class shop(object):
    def __init__(self):
        shoptable = pd.read_csv('C:/Users/Hiroshi Sakai/workspace/Kojitsu/input/shopname.csv',encoding="SHIFT-JIS")
        self.shopdic={}
        for ind,row in shoptable.iterrows():
            self.shopdic.update({int(row.shopcode):row.shopname})
    def getname(self,code):
        return(self.shopdic.get(int(code),'unknown'))

class counter(object):
    def __init__(self,checkpoint):
        self.counter = 0
        self.ck = checkpoint
    def inc(self):
        self.counter+=1
        if self.counter%self.ck == 0:
            print ("Now counter is "+str(self.counter))

def createtable(table):
    table = table.sort_values(['user_id','purchase_date','slip_id'])
    users = set(table.user_id)

    thing_c = CategoricalDtype(sorted(table.jan_code.unique()), ordered=True)
    table.jan_code = table.jan_code.astype(thing_c)
    table.loc[:,'jan_code_codes'] = table.jan_code.astype(thing_c).cat.codes
#    col = table.jan_code.astype(thing_c).cat.codes
    sparse_matrix = dok_matrix((thing_c.categories.size, thing_c.categories.size),dtype = np.csingle)
#    sparse_matrix[:,:] = 0+0j
#    dfs = pd.SparseDataFrame(sparse_matrix, index=thing_c.categories, columns=thing_c.categories,default_fill_value=0)
    
    befnum = (1-1j)/sqrt(2)
    afnum = (1+1j)/sqrt(2)
    coun = counter(1000)
    for user in users:
        userchunk = table[table.user_id == user] # assume the sorted order is preserved
        
        for ind,row in userchunk.iterrows():
            def AddSparse(bef,item,val):
                bef_codes = sorted(set(bef.jan_code_codes))
                if len(bef_codes) > 0:
                    sparse_matrix[item, bef_codes] += val

            date = row.purchase_date
            item = row.jan_code_codes
            AddSparse(userchunk[userchunk.purchase_date> date],item,befnum)
            AddSparse(userchunk[userchunk.purchase_date< date],item,afnum)
            AddSparse(userchunk[userchunk.purchase_date== date],item,1)
            coun.inc()


            
            
if __name__=='__main__':

#    table2 = pd.read_pickle(postempfile)
    table = pd.read_pickle(posfile)
    table = table[table.purchase_date>=pd.Timestamp(2017,1,1)]
    shopset = set(table.shop)
    table.loc[:,'branddept'] = [str(x)+y+str(z) for x,y,z in zip(table.DEPT,table.brand,table.SDEPT) ]
#    table.loc[:, 'branddept'] = [str(x)  + str(z) for x, z in zip(table.DEPT, table.SDEPT)]
    table.loc[:, 'count'] = 1
    num_cluster = 16
#    createtable(table2)
#     u_vec,i_vec = SparsePivot(table2,'user_id','jan_code','count')
#     u_vec,i_vec = SparsePivot(table2,'user_id','purchase_date','price')
    u_vec,i_vec = PivotAndNMF(table,'branddept','purchase_date','count')
    result_dic= {}
    result_dic.update({'all':i_vec})
    base_vec = i_vec
    dic = shop()
    u_index = u_vec.index
    i_index = i_vec.index
    for s in shopset:
        shoptable = table[table.shop==s]
        i_vec = PivotAndNMF_fixedU(shoptable,'branddept','purchase_date','count',i_index,u_vec)
        result_dic.update({dic.getname(s):i_vec})
        base_vec = base_vec.append(i_vec)

#        res = kmeans.predict(i_vec)
#        shop_df = pd.DataFrame(res,index = storind,columns=[dic.getname(s)])
        
#        res_c = pd.concat([res_c,shop_df],axis = 1)

    
#    i_vec = preprocessing.normalize(i_vec)
    kmeans = KMeans(n_clusters=num_cluster, random_state=0).fit(base_vec)
    res = kmeans.predict(result_dic.get('all'))

    '''
    # test cluster counts
    distortions = []
    for i in range(1,20):
        print ("i = "+str(i))
        km = KMeans(n_clusters=i, init='k-means++',random_state=0).fit(base_vec)
        distortions.append(km.inertia_)
    plt.plot(range(1,20),distortions,marker='o')
    plt.xlabel('Number of clusters')
    plt.ylabel("distortion")
    plt.show()
    '''
    storind = i_index
    storind = [x.strftime("%Y-%m-%d %w") for x in storind]
    
    res_c = pd.DataFrame(res,index = storind,columns=['all'])
    res_c = res_c.sort_index()

    for s in shopset:
        res = kmeans.predict(result_dic.get(dic.getname(s)))
        shop_df = pd.DataFrame(res,index = storind,columns=[dic.getname(s)])
        
        res_c = pd.concat([res_c,shop_df],axis = 1)

    plt.pcolor( res_c, cmap='hsv')
    plt.show()

    shop_clusters = KMeans(n_clusters=10, random_state=0).fit(res_c.T)
    res = shop_clusters.predict(res_c.T)
    res_c.loc['order',:] = res.T
    res_c = res_c.sort_values(by='order',axis = 1)
    res_c = res_c.drop(index='order')
    plt.pcolor(res_c, cmap='hsv')
    plt.show()

    res_c.to_excel('cluster.xlsx')

    only_all = res_c.loc[:,'all']
    only_all.index = i_index
    first = only_all[only_all.index<pd.Timestamp(2018,1,1)]
    second = only_all[only_all.index < pd.Timestamp(2019, 1, 1)]
    second = second[second.index>=pd.Timestamp(2018,1,1)]
    third = only_all[only_all.index>=pd.Timestamp(2019, 1, 1)]
    first.index = [x.strftime("%m-%d") for x in first.index]
    second.index = [x.strftime("%m-%d") for x in second.index]
    third.index = [x.strftime("%m-%d") for x in third.index]
    out = pd.concat([first, second,third], axis=1,sort=True)
    plt.pcolor(out, cmap='hsv')
    plt.show()

#    plt.scatter(res_c.index,res_c.cluster)
#    plt.show()
    '''
    for i in range(num_cluster):
        ex = res_c[res_c.cluster==i]
        for j in range(min(10,ex.shape[0])):
            print (" sample in cluster "+str(i)+" is date "+ex.index[j])
    print (type(res),res)
    '''
    
    '''
    table5 = pd.read_pickle(itemdbfile)
    table2 = convert_table(table2)
    table5 = convert_table(table5)

    janinpos = set(table2.jan_code)
    table5 = table5.reset_index()
    janindb = set(table5.jan_code)
    pos_diff = janinpos - janindb
    print ("pos jan count is "+str(len(janinpos)))
    print("jan in db count is "+str(len(janindb)))
    print ("POS only jan count is "+str(len(pos_diff)))
#    nans = (table2.user_id == np.nan)
#    nan_count = nans.sum()
#    print ("nan in user_id is "+str(len(nan_count)))
    table2 = posaddcols(table2)
    table2 = pd.merge(table2,table5,on='jan_code',how='inner')
    table2.cost = table2.cost.fillna(0)

    table2.to_pickle(postempfile2)
    print (table2.columns)
    '''
