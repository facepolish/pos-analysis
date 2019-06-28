import pandas as pd
from bi.dashboard import Campaign_targets

if __name__=='__main__':

    
    table = pd.read_pickle('E:/download/pos.pkl')
    table2 = pd.read_pickle('C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite/bi/data/bi/pos.pkl')
    table3 = pd.read_pickle('J:/Kobe results/workspace/Kojitsu/src/bisite/bi\data/bi/pos.pkl')
    
    init_users = table2.user_id[0:100]
    init_campaign = [1,2,3,4,5,6,7,8]
    
    ca = Campaign_targets(users = init_users,campaign_list = init_campaign)
    
    test_users = ca.total_users()
    print ("added user counts = "+str(len(test_users)))
    ca.add_members(table2.user_id[100:200])
    test_users = ca.total_users()
    print ("added user counts = "+str(len(test_users)))
    
    ca.set_flags_on(table2.user_id[100:200],3)
    test_users = ca.userlist(3)
    print ("id 3 users counts = "+str(len(test_users)))
    
    ca.del_col(3)
    test_users = ca.userlist(3)
    
    



#    tables = table2.sort_values(by="slip_id")
    # check date range
    '''
    min_date = min(table.purchase_date)
    max_date = max(table.purchase_date)
    min_date2 = min(table2.purchase_date)
    max_date2 = max(table2.purchase_date)
    hight = table.shape[0]
    hight2 = table2.shape[0]
    print ("min date is "+str(min_date))
    print ("max date is "+str(max_date))
    print ("record count is "+str(hight))

    print ("min date is "+str(min_date2))
    print ("max date is "+str(max_date2))
    print ("record count is "+str(hight2))

    table_firstday = table[table.purchase_date == min_date]
    print ("count of first day is "+str(table_firstday.shape[0]))
    table_firstday2 = table2[table2.purchase_date == min_date]
    table_firstday3 = table3[table3.purchase_date == min_date]
    print ("count of first day is "+str(table_firstday2.shape[0]))
    print ("count of first day is "+str(table_firstday3.shape[0]))
    table_firstday = table_firstday.sort_values(by="purchase_time")
    table_firstday2 = table_firstday2.sort_values(by="purchase_time")
    table_firstday3 = table_firstday3.sort_values(by="purchase_time")
    table_firstday.to_excel('E:/download/pos.xlsx')
    table_firstday2.to_excel('E:/download/pos2.xlsx')
    table_firstday3.to_excel('E:/download/pos3.xlsx')
    '''

