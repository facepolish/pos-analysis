import matplotlib.pyplot as plt
import pandas as pd
import sqlalchemy
import datetime as dt
#from posenv import posfile,userfile,possource_columns,colnamedic,usersource_columns,usersource_dbname,possource_datecolmns,possource_dbname
#from sqltodf import db_conn,getposdb,getuserdb,colnamedic,possource_columns
import os
def gen_rev_dic(list):
    dic = {}
    for li in list:
        item = colnamedic.get(li)
        dic.update({item:li})
    return(dic)


if __name__=='__main__':
    print(os.environ['PATH'])

    '''
    postable = pd.read_pickle(posfile)
    usertable = pd.read_pickle(userfile)
    print(usertable.columns)
    postable = postable.sort_values(['purchase_date','purchase_time'])
    usertable = usertable.sort_values('registered_date')
    postable1 = postable[0:2000]
    postable2 = postable[0:1000]
    postable1 = postable1.reset_index()
    postable1 = postable1.rename(columns = gen_rev_dic(possource_columns))
    usertable1 = usertable[0:2000]
    usertable2 = usertable[0:1000]
    usertable1 = usertable1.reset_index()
    usertable1 = usertable1.rename(columns = gen_rev_dic(usersource_columns))
    print (postable1.columns)
    print (postable2.columns)
    print (usertable1.columns)
    print (postable2.columns)
    '''




    with db_conn() as connection:
        string1 = "SELECT * FROM ALL_TAB_COLUMNS"
        string2 = "SELECT * FROM ALL_TAB_COLUMNS WHERE  TABLE_NAME ='KJSMBR'"
        string3 = "SELECT * FROM ALL_TAB_COLUMNS WHERE OWNER = 'HITRMD' and TABLE_NAME ='会員購買履歴'"
        string4 = "SELECT * FROM HITRMD.会員購買履歴 WHERE ROWNUM<=10"
        string5 = "SELECT NLS_CHARSET_NAME(NLS_CHARSET_ID('CHAR_CS')),NLS_CHARSET_NAME(NLS_CHARSET_ID('NCHAR_CS')) FROM DUAL"
        string6 = "SELECT * FROM  KJSMBR WHERE ROWNUM<=10"
        string7 = 'SELECT * FROM v$pdbs'
        tablename = "'KJSMBR'"
#        result = connection.execute("alter session set container=posdata")
        '''
        print ('User Tables')
        datestirng = 'AND 売上日付 >= ' +dt.datetime(2019,1,4).strftime('%Y%m%d')
        result = connection.execute(string4+datestirng)
        table = pd.read_sql(string4+datestirng,connection,chunksize =5,parse_dates =possource_datecolmns)
        for row in table:
            print (row)
        '''
        usertable = getuserdb()

        pos = getposdb(newtable= True)
        for i in range(10):
            newpos = getposdb(pos)
            pos = pos.append(newpos)
        '''
        if connection.has_table(possource_dbname):
            print ("yes con has table")
        else:
            print ("no not at all")


        result = connection.execute(string3)
        for row in result:
            print (row)

        print ('All_Tab')

        result = connection.execute(string2)
        for row in result:
            print (row)
        '''

# check DB sampling
        '''
        chunk = pd.read_sql_table(possource_dbname,connection,
            parse_dates = possource_datecolmns,columns=possource_columns,
            chunksize = 100)
        for rows in chunk:
            print (rows)

        chunk = pd.read_sql_table(usersource_dbname,connection,
            columns=usersource_columns,chunksize = 100,schema="HITRMD")
        for rows in chunk:
            print (rows)

        '''


#        iter = pd.read_sql(pos_sql_string,connection,chunksize=100)
#        for row in iter:
#            print (type(row),row.shape)

#        result = connection.execute("SELECT name,open_mode FROM 会員購買履歴")
#        result = connection.execute("SELECT * FROM ALL_TAB_COLUMNS WHERE OWNER = 'HITRMD'")
#        result = connection.execute("alter pluggable database posdata open")
#        result = connection.execute("SELECT * from all_tables order by owner,table_name")
#        result = connection.execute("drop table kojitsupos")
#        result = connection.execute("drop table kojitsuuser")
#        print(result)
'''

        postable1.to_sql('kojitsupos',connection,if_exists='append',
            dtype={'会員番号':sqlalchemy.types.String(length=12)
                   ,'売上日付':sqlalchemy.types.Date()
#                   ,'売上時間': sqlalchemy.types.Time()
                   })
        usertable1.to_sql('kojitsuuser',connection,if_exists='append',
            dtype={'会員番号':sqlalchemy.types.String(length=12)})
    respos = getposdb(postable2)
    resuser = getuserdb(usertable2)
    print ("sql pos hight = "+str(postable1.shape[0]))
    print ("result pos hight = "+str(respos.shape[0]))
    print ("sql user hight = "+str(usertable1.shape[0]))
    print ("result user hight = "+str(resuser.shape[0]))

    for col in respos.columns:
        if not (respos[col].dtype == postable2[col].dtype):
            print ("datatype mismatch")
            print ("columns = "+str(col))
            print ("respos dtype = "+str(respos[col].dtype))
            print ("postable2 dtype = "+str(postable2[col].dtype))
    usertable2 = usertable2.reset_index()
    for col in resuser.columns:
        if not (resuser[col].dtype == usertable2[col].dtype):
            print ("datatype mismatch")
            print ("columns = "+str(col))
            print ("resuser dtype = "+str(resuser[col].dtype))
            print ("usertable2 dtype = "+str(usertable2[col].dtype))
'''
