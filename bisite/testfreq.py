import matplotlib.pyplot as plt
import pandas as pd
from datetime import timedelta,datetime,date

posfile = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/bi/data/bi/old/pos.pkl'
userfile = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/bi/data/bi/user.pkl'
outfile = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/out.xlsx'

def sumnonzero(lis):
    s = sum(lis)
    if s>0:
        return(1)
    else:
        return(0)
    
if __name__=='__main__':

    
    user = pd.read_pickle(userfile)
    usercount = user.groupby('visit_count').count()
    usercount = usercount.loc[:,'user_rank']
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

    postable = pd.read_pickle(posfile)
    userbydate = pd.pivot_table(postable,index='user_id',columns='purchase_date',aggfunc=sumnonzero)
    for ind,row in userbydate.iterrows():
        print ('user = '+row.user_id)
        userbydate.loc[ind,'total'] = sum(row)
    userbydate = userbydate[:,['total']]
    
    
    counttable = userbydate.groupby('total').count()
    print (counttable)
    
