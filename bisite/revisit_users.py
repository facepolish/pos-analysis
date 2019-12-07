from bi.posenv import depttablefile
from bi.posenv import sdepttablefile
#from statistics import mean,median,div
import matplotlib.pyplot as plt
import pandas as pd
from datetime import timedelta,datetime,date
from numba import jit

posfile = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/bi/data/bi/pos.pkl'
userfile = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/bi/data/bi/user.pkl'
outfile = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/fands.xlsx'
outpath = 'C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/'


if __name__=='__main__':

    postable = pd.read_pickle(posfile)
    postable = postable.reset_index()
    user = pd.read_pickle(userfile)
    user = user.reset_index()
    user.registered_date = [datetime.strptime(x,'%Y%m%d') for x in user.registered_date]

    table = postable.sort_values(by=['user_id','purchase_date'])
    totalusercount = len(set(table.user_id))
    print ("total user count is "+str(totalusercount))

    week_begin = pd.Timestamp(2018,12,3)
    print ("beggining date is "+str(week_begin)+" "+str(week_begin.isocalendar()))
    week_end = pd.Timestamp(2018,12,9)
    print ("end date is "+str(week_end)+" "+str(week_end.isocalendar()))

    target_users = user[user.registered_date>=week_begin]
    target_users = target_users[target_users.registered_date<=week_end]
    user_set = set(target_users.user_id)
    target_postable = postable[postable.user_id.isin(user_set)]
    summary = target_postable.groupby("year_week").sum()
    summary = summary[["price"]]
    plt.plot(summary.index,summary.price)
    plt.show()
    summary.to_excel(outpath+"decsales.xlsx")

    processing_usercount = 0

    target_count = 0
    revisit_count = 0

    begindate = pd.Timestamp(2018,12,1)
    enddate =  pd.Timestamp(2018,12,31)

    cur_user = 0
    for ind,row in table.iterrows():
        user = row.user_id
        pdate = row.purchase_date
        if not (cur_user == user):
            processing_usercount+=1
            cur_user = user
            skip_flag = False
            user_first_day = pdate
            user_end_day = user_first_day + timedelta(days=14)
            if processing_usercount%10000 == 0:
                print ("Now processing "+str(processing_usercount))
                print("progress =  " + str(100*processing_usercount/totalusercount)+" %")
            if user_first_day< begindate :
                skip_flag = True
                continue
            elif user_first_day > enddate:
                skip_flag = True
                continue
            else:
                target_count += 1
        else:
            if skip_flag == True:
                continue
            if user_first_day != pdate:
                if pdate > user_end_day:
                    skip_flag = True
                    continue
                else:
                    revisit_count += 1
                    skip_flag = True
                
    print ("total new user count in Dec 2018 = "+str(target_count))
    print ("revisit user count in two weeks = "+str(revisit_count))
