import matplotlib.pyplot as plt
import pandas as pd
from datetime import timedelta,datetime,date
from numba import jit

posfile = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/bi/data/bi/old/pos.pkl'
userfile = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/bi/data/bi/user.pkl'
outfile = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/out.xlsx'
outpath = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/'
freqfile = outpath+'freq.pkl'
fixfreqfile = outpath+'fixfreq.pkl'

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

dayslist = [x for x in range(365*10)]

#@jit
def freq_put (table):
    table = table[['user_id','purchase_date']]
    out_table = pd.DataFrame(0,index = dayslist,columns=dayslist)
    table = table.sort_values(by=['user_id','purchase_date'])
    table = table.reset_index()
    cur_user = 0
    user_counter = 0
    visit_count = 0
#    items = [(x,y) for x,y in zip( table.user_id,table.purchase_date)]
#    for item in items:
#        user = item[0]
#        pdate = item[1]
    for ind,row in table.iterrows():
        user = row.user_id
        pdate = row.purchase_date
        if not(cur_user == user):
            cur_user = user
            visit_count = 1
            user_counter+=1
            last_visit_day = pdate
            if user_counter%10000 == 0:
                print ("Now user count is "+str(user_counter))
                out_table.to_pickle(freqfile)
        if not (last_visit_day == pdate):
            days_passed = pdate - last_visit_day
            out_table.loc[visit_count,days_passed.days] += 1
            visit_count+=1
            last_visit_day = pdate

def fix_freq_put (table):
    table = table[['user_id','purchase_date']]
    out_table = pd.DataFrame(0,index = dayslist,columns=dayslist)
    table = table.sort_values(by=['user_id','purchase_date'])
    table = table.reset_index()
    cur_user = 0
    user_counter = 0
    visit_count = 0
    first_day = 0
#    items = [(x,y) for x,y in zip( table.user_id,table.purchase_date)]
#    for item in items:
#        user = item[0]
#        pdate = item[1]
    for ind,row in table.iterrows():
        user = row.user_id
        pdate = row.purchase_date
        if not(cur_user == user):
            cur_user = user
            visit_count = 1
            user_counter+=1
            first_day = pdate
            last_visit_day = pdate

            if user_counter%10000 == 0:
                print ("Now user count is "+str(user_counter))
                out_table.to_pickle(fixfreqfile)
        if not (last_visit_day == pdate):
            days_passed = pdate - first_day
            out_table.loc[visit_count,days_passed.days] += 1
            visit_count+=1
            last_visit_day = pdate

def check_freq (table,usertable):
    table = table[['user_id','purchase_date']]
    table = table.sort_values(by=['user_id','purchase_date'])
    table = table.reset_index()
    userlist = list(set(table.user_id))
    userlist2 = ['0']
    userlist2.extend(userlist)
    col = ['count']
    user_count = pd.DataFrame(0, index = userlist2, columns=col)
    cur_user = '0'
    user_counter = 0
    visit_count = 0
    mis_match_count = 0
    for ind,row in table.iterrows():
        user = row.user_id
        pdate = row.purchase_date
        if not(cur_user == user):
            user_count.loc[cur_user,'count'] = visit_count
            if (cur_user in usertable.index):
                if not(usertable.loc[cur_user,'visit_count'] == visit_count):
                    mis_match_count += 1
                    mis_ratio = mis_match_count/(user_counter+1)
                    print ("current mismatch ratio is "+str(mis_ratio))
                    
                
            cur_user = user
            visit_count = 1
            user_counter+=1
            last_visit_day = pdate

            if user_counter%10000 == 0:
                print ("Now user count is "+str(user_counter))
                out_table.to_pickle(fixfreqfile)
        if not (last_visit_day == pdate):
            visit_count+=1
            last_visit_day = pdate


def ana_freq ():
    freq_table = pd.read_pickle(freqfile)
    mean_table = pd.DataFrame(0,index=dayslist,columns=['mean','sdiv'])
    for ind in dayslist:
        mean_table.loc[ind,'mean'] = freq_table.loc[ind,:].mean()
        mean_table.loc[ind,'sdiv'] = freq_table.loc[ind,:].std()
        total = freq_table.loc[ind,:].sum()
        mean_table.loc[ind,'total'] =total
        week = freq_table.loc[ind,:7].sum()
        mean_table.loc[ind,'in_a_week'] = week
        biweek = freq_table.loc[ind,:14].sum()
        mean_table.loc[ind,'in_2_weeks'] = biweek
        month = freq_table.loc[ind,:30].sum()
        mean_table.loc[ind,'in_a_month'] = month
        nine  = freq_table.loc[ind,:90].sum()
        mean_table.loc[ind,'in_90_days'] = nine
        half_y = freq_table.loc[ind,:180].sum()
        mean_table.loc[ind,'in_180_days'] = half_y
        y = freq_table.loc[ind,:365].sum()
        mean_table.loc[ind,'in_a_year'] = y
        mean_table.loc[ind,'in_a_week_ratio'] = week/total
        mean_table.loc[ind,'in_2_weeks_ratio'] = biweek/total
        mean_table.loc[ind,'in_a_month_ratio'] = month/total
        
        mean_table.loc[ind,'in_90_ratio'] = nine/total
        mean_table.loc[ind,'in_180_ratio'] = half_y/total
        mean_table.loc[ind,'in_a_year_ratio'] = y/total


    for i in range(10):
        print ("visit count = "+str(i))
        print ("mean next visit interval = "+str(mean_table.loc[i,'mean']))
        print ("std next visit interval = "+str(mean_table.loc[i,'sdiv']))
        plt.plot(dayslist,freq_table.loc[i,:])
        plt.show()
        plt.plot(freq_table.columns[:60],freq_table.loc[i,:59])
        plt.show()
    sub_table = freq_table.loc[:60,:370]
    sub_table.to_excel(outpath+'sub.xlsx')
    sub_table2 = mean_table.loc[:60,:]
    sub_table2.to_excel(outpath+'sub2.xlsx')

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


    postable = pd.read_pickle(posfile)
    user = pd.read_pickle(userfile)
    check_freq(postable,user)

    '''    
    fix_freq = pd.read_pickle(fixfreqfile)
    total_freq = pd.DataFrame(0,index = ['total'],columns=dayslist)
    daylist2 = dayslist[:500]
    for i in range(10):
        title = str(i+1)+" 回目の購買"
        plt.title(title)
        plt.plot(dayslist,fix_freq.loc[i,:])
        plt.show()
        title = title +" 500日まで"
        plt.title(title)
        plt.plot(daylist2,fix_freq.loc[i,:499])
        plt.show()
        total_freq.loc['total',:] += fix_freq.loc[i,:]

    title = str(i+1)+"合算"
    plt.title(title)
    plt.plot(dayslist,fix_freq.loc[i,:])
    plt.show()
    title = str(i+1)+"合算　５００日まで"

    plt.plot(daylist2,fix_freq.loc[i,:499])
    plt.show()
    '''

    summary = fix_freq.ix[:10,:]
    summary.to_excel(outpath+'summ.xlsx')

#    ana_freq()
#    postable = pd.read_pickle(posfile)
#    freq_put(postable)
    

    '''
    user = pd.read_pickle(userfile)
    usercount = user.groupby('visit_count').count()
    usercount = usercount.loc[:,'user_rank']
    count_table(usercount,'out.xlsx')
    print (user.columns)
    regionlist = set(user.address)
    print (regionlist)
    postable = pd.read_pickle(posfile)
    userbydate = pd.pivot_table(postable,index='user_id',columns='purchase_date',aggfunc=visit_count)
    count_table(userbydate.purchase_date,'out2.xlsx')
    
    postable.loc[:,'day_price'] = [(i,j) for i,j in zip(postable.purchase_date,postable.price)]
    '''
    

    
