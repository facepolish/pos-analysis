import pandas as pd
import os
from sqlalchemy import create_engine
from datetime import timedelta
import contextlib
from posenv import col_dtype,colnamedic,possource_columns,usersource_columns
from tableclass import posaddcols

db_settings = {
    "host":'localhost',
    "database":'kojitsu',
    "user":'SYSTEM',
    "password":'sakaI123',
    "port":'1521'
}
def col_str (lis):
    st = ''
    for i in range(0,len(lis)-1):
        st = st+lis[i]+','
    st=st+lis[len(lis)-1]
    return (st)

@contextlib.contextmanager
def db_conn():
    try:
        os.environ['NLS_LANG'] = 'JAPANESE_JAPAN.UTF8'
        engine = create_engine("oracle://{user}:{password}@{host}:{port}/{database}".format(**db_settings) ,echo=True)
        connection = engine.connect()
        result = connection.execute("alter session set container=posdata")
        yield connection
    finally:
        connection.close()
        
def prev_dat(d):
    day_before_max = d - timedelta(days=1)
    day_string = day_before_max.strftime("%Y/%m/%d")
    return(day_string)
    
def convert_table(table):
    for col in table.columns:
        ty = col_dtype.get(col,0)
        if not (ty == 0):
            table.loc[:,col] = table.loc[:,col].astype(ty)
    return(table)


def getposdb(posdb=None):
    if posdb==None:
        pos_sql_string = "select {pos_col} from kojitsupos".format(pos_col=col_str(possource_columns))
    else:
        maxdate = max(posdb.purchase_date)
        maxdatepos = posdb.query('purchase_date==@maxdate')
        maxtime = max(maxdatepos.purchase_time)
        date_string = prev_dat(maxdate)
        pos_sql_string = "select {pos_col} from kojitsupos where {key_col} > to_date('{pos_day}','yyyy/mm/dd')".format(pos_col=col_str(possource_columns),pos_day=date_string,key_col=possource_columns[0])
    with db_conn() as connection:
        sqlpos = pd.read_sql(pos_sql_string,connection)
    sqlpos = sqlpos.rename(columns = colnamedic)
    sqlpos1 = sqlpos.query('purchase_date> @maxdate')
    sqlpos2 = sqlpos.query('purchase_date==@maxdate')
    sqlpos2 = sqlpos2.query('purchase_time > @maxtime')
    sqlpos = pd.concat([sqlpos2,sqlpos1])
    sqlpos = posaddcols(sqlpos)
    sqlpos = convert_table(sqlpos)

    return(sqlpos)

def getuserdb(userdb=None):
    if userdb == None:
        user_sql_string = "select {user_col} from kojitsuuser".format(user_col=col_str(usersource_columns))
    else:
        maxdate = max(userdb.registered_date)
        mindate = min(userdb.registered_date)
        date_string = prev_dat(maxdate)
        user_sql_string = "select {user_col} from kojitsuuser where {key_col} > to_date('{user_day}','yyyy/mm/dd')".format(user_col=col_str(usersource_columns),user_day=date_string,key_col=usersource_columns[0])
    with db_conn() as connection:
        sqluser = pd.read_sql(user_sql_string,connection)
    sqluser = sqluser.rename(columns = colnamedic)

    setsqluser = set(sqluser.user_id)
    setuserdb = set(userdb.index)
    comm = setsqluser & setuserdb
    remains = setsqluser - comm
    sqluser = sqluser[sqluser.user_id.isin(remains)]
    sqluser = convert_table(sqluser)

    return(sqluser)
