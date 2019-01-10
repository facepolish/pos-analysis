import pandas as pd
from scipy.sparse import csr_matrix
from pandas.api.types import CategoricalDtype
from sklearn.decomposition import NMF
import numpy as np
uservecfile='data/bi/uservec.pkl'
itemvecfile='data/bi/itemvec.pkl'
samecartitemvecfile='data/bi/samecartitemvec.pkl'
posfile='data/bi/pos.pkl'
import numpy as np
import math
from sklearn.preprocessing import normalize
def update_uv(M, U, V):
    divu = np.dot(U,np.dot(V.T, V))
    divu = np.where(divu == 0,0.1,divu)
    U = U * M.dot(V) / divu
    divv = np.dot(np.dot(U.T, U), V.T).T
    divv = np.where(divv == 0,0.1,divv)
    V = V * (M.T).dot(U) / divv
    return U, V

def SparseNMF(sparse_matrix):
    k = 16
    m = sparse_matrix.shape[0]
    n = sparse_matrix.shape[1]
    U = np.abs(np.random.uniform(low=0,high=1,size=(m,k)))
    V = np.abs(np.random.uniform(low=0,high=1,size=(n,k)))
    iters = 10000
    minU = 1000
    ng_max = 100
    ng_count = 0
    for _ in range(iters):
        print('count = '+str(_))
        lastU = U
        lastV = V
        U, V = update_uv(sparse_matrix, U, V)
        lastU = U - lastU
        diffU = np.linalg.norm(lastU)
        nrmU = np.linalg.norm(U)

        lastV = V - lastV
        diffV = np.linalg.norm(lastV)
        nrmV = np.linalg.norm(V)
        diffall = diffU*diffV
        print ('result norm U is '+str(nrmU)+' and diff norm is '+str(diffU))
        print ('result norm V is '+str(nrmV)+' and diff norm is '+str(diffV))
        print ('diffall = '+str(diffall))
        if diffall<minU:
            minU = diffall
            optU = U
            ng_count=0
        else:
            ng_count+=1
            print ('ng_count = '+str(ng_count))
            if ng_count>ng_max:
                break
    U = normalize(U,axis=1)
    V = normalize(V,axis=1)
    return(U,V)
    
def SparsePivot(table,index_label,col_label,val_label):
    person_c = CategoricalDtype(sorted(table.loc[:,index_label].unique()),ordered=True)
    thing_c = CategoricalDtype(sorted(table.loc[:,col_label].unique()),ordered=True)
    row = table.loc[:,index_label].astype(person_c).cat.codes
    col = table.loc[:,col_label].astype(thing_c).cat.codes
    sparse_matrix = csr_matrix((table[val_label],(row,col)),
                                shape=(person_c.categories.size,thing_c.categories.size))
    dfs = pd.SparseDataFrame(sparse_matrix,index=person_c.categories,columns=thing_c.categories,default_fill_value=0)
    return(sparse_matrix,dfs)

class ItemRecommend(object):
    def __init__(self):
        self.item_vec = pd.read_pickle(itemvecfile)
        self.samecartitem_vec = pd.read_pickle(samecartitemvecfile)
        self.user_vec = pd.read_pickle(uservecfile)
    def update(self,table):
        table.loc[:,'count'] = 1
        table.loc[:,'cartid'] = table.user_id+table.year_week
        
        sparse_matrix,dfs = SparsePivot(table,'user_id','itemid','count')
        
        U,V = SparseNMF(sparse_matrix)

        self.user_vec = pd.DataFrame(U,index = dfs.index)
        self.item_vec = pd.DataFrame(V,index = dfs.columns)
        self.item_vec.to_pickle(itemvecfile)
        self.user_vec.to_pickle(uservecfile)

        sparse_matrix,dfs = SparsePivot(table,'cartid','itemid','count')
        
        U,V = SparseNMF(sparse_matrix)

    #    user_vec = pd.DataFrame(U,index = dfs.index)
        self.samecartitem_vec = pd.DataFrame(V,index = dfs.columns)
        self.samecartitem_vec.to_pickle(samecartitemvecfile)

    def __getrecommend(self,vecs,item):
        item_vec = vecs.loc[item,:]
        metrics = item_vec.dot(vecs.values.T)
        table = pd.DataFrame(metrics,index=vecs.index,columns=['score'])
        table = table.sort_values('score',ascending=False)
        return table
    
    def getsamecartrecommendlist(self,item):
        return self.__getrecommend(self.samecartitem_vec,item)

    def getsamecustomerrecommendlist(self,item):
        return self.__getrecommend(self.item_vec,item)

if __name__=='__main__':
    table = pd.read_pickle(posfile)
    it_rec = ItemRecommend()
    it_rec.update(table)
    
    sampleitem = table.loc[table.index[10],'itemid']
    print ('sample item is '+sampleitem)
    list = it_rec.getsamecartrecommendlist(sampleitem)
    print ('same cart recommends are')
    print (list[1:11])

    list = it_rec.getsamecustomerrecommendlist(sampleitem)
    print ('Customer based recommends are')
    print (list[1:11])
    
