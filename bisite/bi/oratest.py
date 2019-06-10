import matplotlib.pyplot as plt
import pandas as pd
import sqlalchemy
from posenv import posfile,userfile
from sqltodf import db_conn,getposdb,getuserdb,colnamedic,possource_columns,usersource_columns

def gen_rev_dic(list):
    dic = {}
    for li in list:
        item = colnamedic.get(li)
        dic.update({item:li})
    return(dic)

    
if __name__=='__main__':

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
    
    


    with db_conn() as connection:
#        result = connection.execute("SELECT name,open_mode FROM v$pdbs")
#        result = connection.execute("alter pluggable database posdata open")
#        result = connection.execute("SELECT * from all_tables order by owner,table_name")
        result = connection.execute("drop table kojitsupos")
        result = connection.execute("drop table kojitsuuser")
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
