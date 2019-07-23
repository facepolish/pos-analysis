import pandas as pd
import pickle
from scipy.sparse import csr_matrix
from pandas.api.types import CategoricalDtype
from sklearn.decomposition import NMF
import numpy as np
import os
from .posenv import uservecfile,itemvecfile,posfile,deptuserfile,sdeptvecfile,sdeptuserfile,samecartitemvecfile,deptvecfile,depttablefile,brandvecfile,branduservecfile

deptfile=depttablefile

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
def PivotAndNMF(table, ind, col, how):
    sparse_matrix, dfs = SparsePivot(table, ind, col, how)
    U, V = SparseNMF(sparse_matrix)
    u_vec = pd.DataFrame(U, index=dfs.index)
    i_vec = pd.DataFrame(V, index=dfs.columns)
    return (u_vec, i_vec)

def DEPTSDEPTcode (dept,sdept):
    return(str(dept).zfill(2)+str(sdept).zfill(3))


def vec_update(table):
    table.loc[:, 'count'] = 1
    table.loc[:, 'DEPTSDEPT'] = [DEPTSDEPTcode(x,y) for x, y in zip(table.DEPT, table.SDEPT)]

    if not (os.path.exists(uservecfile)) or not (os.path.exists(itemvecfile)):
        user_vec, item_vec = PivotAndNMF(table, 'user_id', 'jan_code', 'price')
        item_vec.to_pickle(itemvecfile)
        user_vec.to_pickle(uservecfile)

    if not (os.path.exists(samecartitemvecfile)):
        _, samecartitem_vec = PivotAndNMF(table, 'receit_id', 'jan_code', 'count')
        samecartitem_vec.to_pickle(samecartitemvecfile)

    if not (os.path.exists(deptvecfile)) or not (os.path.exists(deptuserfile)):
        deptuser_vec, dept_vec = PivotAndNMF(table, 'user_id', 'DEPT', 'price')
        dept_vec.to_pickle(deptvecfile)
        deptuser_vec.to_pickle(deptuserfile)
    if not (os.path.exists(sdeptvecfile)) or not (os.path.exists(sdeptuserfile)):
        sdeptuser_vec, sdept_vec = PivotAndNMF(table, 'user_id', 'DEPTSDEPT', 'price')
        sdept_vec.to_pickle(sdeptvecfile)
        sdeptuser_vec.to_pickle(sdeptuserfile)

class ItemRecommend(object):

    def __init__(self,newfile=False):
        if not(newfile == True):
            self.item_vec = pd.read_pickle(itemvecfile)
            self.user_vec = pd.read_pickle(uservecfile)
            self.samecartitem_vec = pd.read_pickle(samecartitemvecfile)
            self.sdept_vec = pd.read_pickle(sdeptvecfile)
            self.sdeptuser_vec = pd.read_pickle(sdeptuserfile)
            self.dept_vec = pd.read_pickle(deptvecfile)
            self.deptuser_vec = pd.read_pickle(deptuserfile)
            self.brand_vec = pd.read_pickle(brandvecfile)
            self.branduser_vec = pd.read_pickle(branduservecfile)

    def __getrecommend(self,vecs1,vecs2,item):
        if not(item in vecs1.index):
            nulind = []
            table = pd.DataFrame(0, index=nulind, columns=['score'])
            return(table)

        item_vec = vecs1.loc[item,:]

        metrics = item_vec.dot(vecs2.values.T)
        table = pd.DataFrame(metrics,index=vecs2.index,columns=['score'])
        avg = table.score.mean()
        table = table[table.score>=avg]
        table = table.sort_values('score',ascending=False)
#        table = table.reset_index()
        return table

    def getsamecartrecommendlist(self,item):
        return self.__getrecommend(self.samecartitem_vec,self.samecartitem_vec,item)

    def getsamecustomerrecommendlist(self,item):
        return self.__getrecommend(self.item_vec,self.item_vec,item)

    def getdeptrecommenduserlist(self,userlist,dept):
        user_vec = self.deptuser_vec[self.deptuser_vec.index.isin(userlist)]
        return self.__getrecommend(self.dept_vec,user_vec,dept)

    def getsdeptrecommenduserlist(self,dept,sdept):
        id = DEPTSDEPTcode(dept,sdept)
        return self.__getrecommend(self.sdept_vec,self.sdeptuser_vec,id)

    def getbrandrecommenduserlist(self,userlist,brand):
        user_vec = self.branduser_vec[self.branduser_vec.index.isin(userlist)]
        return self.__getrecommend(self.brand_vec,user_vec,brand)

        
    def vec_update(self,table):
        table.loc[:, 'count'] = 1
        table.loc[:, 'cartid'] = table.user_id + table.year_week
        table.loc[:, 'DEPTSDEPT'] = [DEPTSDEPTcode(x,y) for x, y in zip(table.DEPT, table.SDEPT)]

        self.user_vec, self.item_vec = PivotAndNMF(table, 'user_id', 'jan_code', 'price')
        self.item_vec.to_pickle(itemvecfile)
        self.user_vec.to_pickle(uservecfile)

        _, self.samecartitem_vec = PivotAndNMF(table, 'cartid', 'jan_code', 'count')
        self.samecartitem_vec.to_pickle(samecartitemvecfile)
        tablefdept = table.dropna(subset=['DEPT'])
        self.deptuser_vec, self.dept_vec = PivotAndNMF(tablefdept, 'user_id', 'DEPT', 'price')
        self.dept_vec.to_pickle(deptvecfile)
        self.deptuser_vec.to_pickle(deptuserfile)
        self.sdeptuser_vec, self.sdept_vec = PivotAndNMF(table, 'user_id', 'DEPTSDEPT', 'price')
        self.sdept_vec.to_pickle(sdeptvecfile)
        self.sdeptuser_vec.to_pickle(sdeptuserfile)
        tablefbrand = table.dropna(subset=['brand'])
        self.branduser_vec, self.brand_vec = PivotAndNMF(tablefbrand, 'user_id', 'brand', 'count')
        self.brand_vec.to_pickle(brandvecfile)
        self.branduser_vec.to_pickle(branduservecfile)

    def vec_update2(self,table):
        table.loc[:, 'count'] = 1
        table.loc[:, 'cartid'] = table.user_id + table.year_week
        table.loc[:, 'DEPTSDEPT'] = [DEPTSDEPTcode(x,y) for x, y in zip(table.DEPT, table.SDEPT)]
        '''
        self.user_vec, self.item_vec = PivotAndNMF(table, 'user_id', 'jan_code', 'price')
        self.item_vec.to_pickle(itemvecfile)
        self.user_vec.to_pickle(uservecfile)

        _, self.samecartitem_vec = PivotAndNMF(table, 'cartid', 'jan_code', 'count')
        self.samecartitem_vec.to_pickle(samecartitemvecfile)
        '''
        tablefdept = table.dropna(subset=['DEPT'])
        self.deptuser_vec, self.dept_vec = PivotAndNMF(table, 'user_id', 'DEPT', 'price')
        self.dept_vec.to_pickle(deptvecfile)
        self.deptuser_vec.to_pickle(deptuserfile)
        self.sdeptuser_vec, self.sdept_vec = PivotAndNMF(tablefdept, 'user_id', 'DEPTSDEPT', 'price')
        self.sdept_vec.to_pickle(sdeptvecfile)
        self.sdeptuser_vec.to_pickle(sdeptuserfile)

        tablefbrand = table.dropna(subset=['brand'])
        self.branduser_vec, self.brand_vec = PivotAndNMF(tablefbrand, 'user_id', 'brand', 'count')
        self.brand_vec.to_pickle(brandvecfile)
        self.branduser_vec.to_pickle(branduservecfile)




if __name__=='__main__':
    f=open(deptfile,'rb')
    lis=pickle.load(f)
    print(lis)
#    posfile = "c:/Users/ttmuyn/workspace/Kojitsu/src/bisite/bi/data/bi/pos.pkl"
    table = pd.read_pickle(posfile)
#    vec_update(table)
    it_rec = ItemRecommend()
    it_rec.vec_update(table)

    sampleitem = table.loc[table.index[10],'jan_code']
    print ('sample item is '+sampleitem)
    list = it_rec.getsamecartrecommendlist(sampleitem)
    print ('same cart recommends are')
    print (list[1:11])

    list = it_rec.getsamecustomerrecommendlist(sampleitem)
    print ('Customer based recommends are')
    print (list[1:11])
