import os
from pathlib import Path

#from django.conf import settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

posfile = os.path.join(BASE_DIR, 'bi/data/bi/pos.pkl')
userfile = os.path.join(BASE_DIR, 'bi/data/bi/user.pkl')
uservecfile = os.path.join(BASE_DIR, 'bi/data/bi/uservec.pkl')
itemvecfile = os.path.join(BASE_DIR, 'bi/data/bi/itemvec.pkl')
itemiddicfile = os.path.join(BASE_DIR, 'bi/data/bi/itemid.pkl')
depttablefile = os.path.join(BASE_DIR, 'bi/data/bi/dept.pkl')
sdepttablefile = os.path.join(BASE_DIR, 'bi/data/bi/sdept.pkl')
deptsdepttablefile = os.path.join(BASE_DIR, 'bi/data/bi/deptsdept.pkl')
itemdbfile = os.path.join(BASE_DIR, 'bi/data/bi/itemdb.pkl')
campaign_target_file = os.path.join(BASE_DIR, 'bi/data/bi/campaign_targets.pkl')
campaign_cache_file = os.path.join(BASE_DIR, 'bi/data/bi/campaign_cache.pkl')

deptvecfile=os.path.join(BASE_DIR, 'bi/data/bi/deptvec.pkl')
deptuserfile=os.path.join(BASE_DIR, 'bi/data/bi/deptuser.pkl')
sdeptvecfile=os.path.join(BASE_DIR, 'bi/data/bi/sdeptvec.pkl')
sdeptuserfile=os.path.join(BASE_DIR, 'bi/data/bi/sdeptuser.pkl')
samecartitemvecfile=os.path.join(BASE_DIR, 'bi/data/bi/samecartitemvec.pkl')
brandvecfile=os.path.join(BASE_DIR, 'bi/data/bi/brandvec.pkl')
branduservecfile=os.path.join(BASE_DIR, 'bi/data/bi/branduservec.pkl')

kojitsupath = Path(BASE_DIR).parent.parent

recencyfile=os.path.join(BASE_DIR, 'bi/data/bi/recency.pkl')


possource_columns = ['売上日付','店舗ｺｰﾄﾞ','売上時刻','会員番号','型名',#'DEPT','SDEPT','ﾌﾞﾗﾝﾄﾞ',
                     '売価','数量','売上伝票番号','ﾒｰｶｰｺｰﾄﾞ','JANｺｰﾄﾞ'] #'原価',,
possource_dbname = 'HITRMD.会員購買履歴'
possource_datecolmns = ['売上日付','売上時間']
usersource_columns = ['入会年月日','カード番号','都道府県','性別','年齢','年代','来店回数','会員ランク']
usersource_dbname = "HITRMD.KJSMBR"
schema_name = 'HITRMD'

colnamedic = {u'店舗ｺｰﾄﾞ':'shop',
              u'店名':'shop_name',
              u'売上日付':'purchase_date',
              u'注文日':'purchase_date',
              u'受注日':'purchase_date',# genesis order table
              u'受注番号':'order_code', # genesis order table & AcceptDetail. key for Merge
              u'売上時間':'purchase_time',
              u'売上時刻': 'purchase_time',
              u'会員カード番号':'user_id',
              u'カード番号':'user_id',
              u'会員番号':'user_id',
              u'生年月日':'birth_date',
              u'顧客コード':'user_code', # genesis customer table & order table
              u'ブランド':'brand',
              u'ﾌﾞﾗﾝﾄﾞ':'brand',
              u'型名':'type',
              u'商品名':'item_name',
              u'商品名_漢字':'item_name',
              u'金額(税込)':'price', # genesis order table
#              u'商品金額合計':'price',
              u'注文金額合計':'price',  #ECbeing sales
              u'売価':'price', # pos table
              u'数量':'amount',
              u'都道府県':'address',
              u'性別':'gender',
              u'年齢':'age',
              u'年代':'age_group',
              u'来店回数':'visit_count',
              u'仮登録日':'registered_date',
              u'入会年月日':'registered_date',
              u'会員ランク':'user_rank',
              u'分類名':'category',
              u'商品コード':'itemcode',
              u'品番名':'item_code1',
              u'ショップコード':'shop_code',
              u'カテゴリーコード':'categorycode',
              u'カテゴリコード':'categorycode',
              u'【ecbeing】カテゴリコード':'categorycode',
              u'【genesis】商品分類1+2+3':'genesis',
              u'商品分類1コード':'itemcode1',
              u'商品分類2コード':'itemcode2',
              u'商品分類3コード':'itemcode3',
              u'売上額':'price',
              u'POS販売時刻':'purchase_time',
              u'売上伝票番号':'slip_id',
              u'原価':'cost',
              u'ﾒｰｶｰｺｰﾄﾞ':'maker_code',
              u'ﾒｰｶｰ名_漢字':'brand',
              u'生年月':'birth_year_month',
              'dept':'DEPT',
              's_dept':'SDEPT',
              'S_DEPT':'SDEPT',
              'sdept':'SDEPT',
              u'JANｺｰﾄﾞ':'jan_code',}


col_dtype = {
    'user_id':str,
    'user_rank':str,
    'shop_code':str,
    'categorycode':str,
    'itemcode1':str,
    'itemcode2':str,
    'itemcode3':str,
    'itemcode':str,
    'type':str,
    'cost':int,
    'price':int,
    'receit_id':str,
    'maker_code':str,
    'jan_code':str }

_col_dtype_temp = {}
for k,v in colnamedic.items():
    type = col_dtype.get(v,0)
    if not(type == 0):
        _col_dtype_temp.update({k:type})
col_dtype.update(_col_dtype_temp)

gradedic = {'1合目登頂中': '1', '4合目登頂中': '2', '6合目登頂中': '3', '8合目登頂中': '4', '登頂達成！': '5'}

'''
db_settings = {
    "host":'192.168.1.13',
    "database":'ORCL',
#'HITRMD',
    "user":'mduser',
    "password":'mduser',
    "port":'1521'
}
DB_OFFLINE = False
'''
db_settings = {
    "host":'localhost',
    "database":'kojitsu',
    "user":'SYSTEM',
    "password":'sakaI123',
    "port":'1521'
}
DB_OFFLINE = True

