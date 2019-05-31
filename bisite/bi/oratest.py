import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from datetime import timedelta
posfile = os.path.join('C:/Users/Hiroshi Sakai/workspace/Kojitsu/src/bisite', 'bi/data/bi/pos.pkl')

if __name__=='__main__':

    Session = sessionmaker()
    os.environ['NLS_LANG'] = 'JAPANESE_JAPAN.UTF8'
    engine = create_engine("oracle://SYSTEM:sakaI123@localhost:1521/kojitsu" ,echo=True)
    connection = engine.connect()
    result = connection.execute("SELECT name,open_mode FROM v$pdbs")
#    result = connection.execute("alter pluggable database posdata open")
    result = connection.execute("alter session set container=posdata")
    result = connection.execute("SELECT * from all_tables order by owner,table_name")
    postable = pd.read_pickle(posfile)
    postable = postable[0:10000]
    maxdate = max(postable.purchase_date)
    day_before_max = maxdate - timedelta(days=1)
    day_string = day_before_max.strftime("%Y/%m/%d")
    print (day_string)
    sql_string = "select user_id,price from kojitsupos where purchase_date > to_date('{}','yyyy/mm/dd')".format(day_string)
    print (sql_string)
    result = connection.execute("drop table kojitsupos")
    postable.to_sql('kojitsupos',connection,if_exists='append')
#    sqlpos = pd.read_sql(sql_string,connection)
    sqlpos = pd.read_sql("select * from kojitsupos",connection)
    for ind,row in sqlpos.iterrows():
        print(row)

#    for row in result:
#        print(row)
    connection.close()
    Session.configure(bind=engine)
    session = Session()
    session.close()

