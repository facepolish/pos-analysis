import matplotlib.pyplot as plt
import pandas as pd
from datetime import timedelta,datetime,date
from numba import jit

posfile = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/bi/data/bi/old/pos.pkl'
userfile = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/bi/data/bi/user.pkl'
outfile = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/out.xlsx'
outpath = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/'

def sumnonzero(lis):
    s = sum(lis)
    if s>0:
        return(1)
    else:
        return(0)

def firstvisit(lis):
    fis = min(lis)
    return(lis) 

@jit
def visit_count(lis):
    lis.sort()
    counter =0
    fir_ite = lis[0]
    for ite in lis:
        if fir_ite == ite:
            continue
        else:
            counter += 1
            fir_ite = ite
    return(counter)

def first_purchase(lis):
    lis.ort()
    sumfirst=0
    firstday = lis[0][0]
    for ite in lis:
        if ite[0] == firstday:
            sumfirst+=ite[1]
        else:
            break
    return(sumfirst)
    
def count_table(lis,name):
    outfile = outpath+name
    pro = pd.DataFrame(0,index=['pro'],columns=['stub'])
    print (usercount)
    for i in range(len(usercount.index)-1):
        print (' i = '+str(i))
        ups = usercount[i+1:]
        sum1 = sum(ups)
        print("sum1 = "+str(sum1))
        downs = usercount[i:]
        sum2 = sum(downs)
        print("sum2 = "+str(sum2))
        trp = sum1/sum2
        trp = trp*100
        pro.loc['pro',str(i)] = trp
        print ('transition probability is '+str(trp))
    pro.to_excel(outfile)

if __name__=='__main__':

    user = pd.read_pickle(userfile)
    '''
    usercount = user.groupby('visit_count').count()
    usercount = usercount.loc[:,'user_rank']
    count_table(usercount,'out.xlsx')
    '''
    print (user.columns)
    regionlist = set(user.address)
    print (regionlist)
    '''
    postable = pd.read_pickle(posfile)
    userbydate = pd.pivot_table(postable,index='user_id',columns='purchase_date',aggfunc=visit_count)
    count_table(userbydate.purchase_date,'out2.xlsx')
    
    postable.loc[:,'day_price'] = [(i,j) for i,j in zip(postable.purchase_date,postable.price)]
    '''
    

    
