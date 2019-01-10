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

def user_age(list,utable,s):
    utable_web_pos = utable[utable.index.isin(list)]
    average_age = utable_web_pos.age.mean()
    print ("average age of "+s+' is = '+str(average_age))
    plt.hist(utable_web_pos.age,bins = 50)
    plt.title("Age of "+s)
    plt.show()
    
def salessummary(table,s):
    dayscol = ['user_id','purchase_date']
    localtable = table.loc[:,['user_id','price','purchase_date']]

    gtable = localtable.groupby('user_id').sum()
    average = gtable.price.mean()
    print(s+" mean = "+str(average))
    plt.hist(gtable.price,bins = 50)
    plt.title("Per Purchase of "+s)
    plt.show()
    localtable = localtable.sort_values(by = dayscol)
    count_table = localtable.loc[:,dayscol]
    c_agg = count_table.groupby('user_id').agg(tb.count_days)
    average = c_agg.purchase_date.mean()
    print(s+" visit count mean = "+str(average))
    
    
    return(gtable)
     
if __name__=='__main__':
    depttable = tb.DEPTtable('HITRMD_DEPT')
    
    pos17= tb.postable(tb.posnamelist[6])
    pos17= pos17.table
    web17 = tb.websalestable(2017)
    web17 = web17.table
    allsales17 = pos17.append(web17)
    ut = tb.UserTable('cleanutable')
    utable = ut.usertable
    
    
    posusers = set(pos17.user_id)
    webusers = set(web17.user_id)
    poswebusers = posusers & webusers
    posonlyusers = posusers - poswebusers
    webonlyusers = webusers - poswebusers
    
    print("Web & Pos = "+str(len(poswebusers)))
    print("Web only  = "+str(len(webonlyusers)))
    print("Pos only  = "+str(len(posonlyusers)))
    
    user_age(poswebusers,utable,'POS and WEB')
    user_age(posonlyusers,utable,'POS only')
    user_age(webonlyusers,utable,'WEB only')
    
    
    posonlysales = pos17[pos17.user_id.isin(posonlyusers)]
    webonlysales = web17[web17.user_id.isin(webonlyusers)]
    
    salessummary(posonlysales,'POS only')
    salessummary(webonlysales,'WEB only')


    dualposonlysales = pos17[pos17.user_id.isin(poswebusers)]
    dualwebonlysales = web17[web17.user_id.isin(poswebusers)]
    powebsonlysales = salessummary(dualposonlysales,'POS sales of dual users')
    webposonlysales = salessummary(dualwebonlysales,'WEB sales of dual users')
    
    powebsonlysales = powebsonlysales.rename(columns = {'price':'posprice'})
    webposonlysales = webposonlysales.rename(columns = {'price':'webprice'})

    webposonlysales = webposonlysales.join(powebsonlysales)
    webposonlysales.loc[:,'price'] = webposonlysales.loc[:'webprice']+webposonlysales.loc[:,'posprice']
    webposonlysales.price = webposonlysales.webprice+webposonlysales.posprice
    average = webposonlysales.price.mean()
    print("web pos mean = "+str(average))

    dept_col = ['DEPT','price']
    all17 = pos17.loc[:,dept_col]
    banchmarkdept = all17.groupby('DEPT').sum()
    banchmarkdept = banchmarkdept.rename(columns = {'price':'benchmark'})
    posonlysales = posonlysales.loc[:,dept_col]
    posonlydept = posonlysales.groupby('DEPT').sum()
    posonlydept = posonlydept.rename(columns = {'price':'POSONLY'})

    dualposonlysales = dualposonlysales.loc[:,dept_col]
    bothposdept = dualposonlysales.groupby('DEPT').sum()
    bothposdept = bothposdept.rename(columns = {'price':'DUALPOS'})

    banchmarkdept = banchmarkdept.join(posonlydept)
    banchmarkdept = banchmarkdept.join(bothposdept)
    banchmarkdept.rename(index = depttable.namedic,inplace=True)
    banchmarkdept.to_csv(tb.filepos+'posDEPT.csv')


    dept_col = ['eccode','price']
    cat_table = pd.read_csv('C:/Users\Hiroshi Sakai/workspace\Kojitsu/input/webshop/ecbeingcategory.csv',dtype={'categorycode':str})
    namedic = {}
    for ind,item in cat_table.iterrows():
        namedic.update({item.categorycode:item.categoryname})

    all17 = web17.loc[:,dept_col]
    banchmarkdept = all17.groupby('eccode').sum()
    banchmarkdept = banchmarkdept.rename(columns = {'price':'benchmark'})

    webonlysales = webonlysales.loc[:,dept_col]
    webonlydept = webonlysales.groupby('eccode').sum()
    webonlydept = webonlydept.rename(columns = {'price':'WEBONLY'})

    dualwebonlysales = dualwebonlysales.loc[:,dept_col]
    bothwebdept = dualwebonlysales.groupby('eccode').sum()
    bothwebdept = bothwebdept.rename(columns = {'price':'DUALWEB'})

    
    banchmarkdept = banchmarkdept.join(webonlydept)
    banchmarkdept = banchmarkdept.join(bothwebdept)
    banchmarkdept.rename(index = namedic,inplace = True)
    banchmarkdept.to_csv(tb.filepos+'webECCODE.csv')

