import pandas as pd
import datetime
from tableclass import postable, UserTable
path1="C:/Users/Hiroshi Sakai/workspace/Kojitsu/input/57期分析用資料/実店舗/"
file1="会員購買履歴_57期一四半期.xlsx"
file2="会員購買履歴_57期二四半期.xlsx"
file3 = "会員購買履歴_57期三四半期.xlsx"
file4 = "会員購買履歴_57期四四半期.xlsx"
filelist = [file1,file2,file3,file4]

path2 = "C:/Users/Hiroshi Sakai/workspace/Kojitsu/input/メーカーコード・商品マスタ/"
path3 = "C:/Users/Hiroshi Sakai\workspace/Kojitsu/input/57期分析用資料\WebShop\顧客/"

file5 = "商品マスタ.xlsx"
file6 = "HITRMD_ﾒｰｶｰｺｰﾄﾞ.xlsx"
file7 = "customer190124最新.xlsx"

col_dtype_new = {'user_id':str,'user_rank':str}
col_dtype = {u'会員番号':str,u'会員カード番号':str,'user_id':str,'user_rank':str,u'商品コード':str,u'カテゴリコード':str,u'カテゴリーコード':str,u'ショップコード':str, u'商品分類1コード':str,u'商品分類2コード':str,u'商品分類3コード':str,'user_id':str,'user_rank':str} 

colnamedic_pos = {u'会員番号':'user_id'}
colnamedic = {u'店舗ｺｰﾄﾞ':'shop',
              u'店名':'shop_name',
              u'売上日付':'purchase_date',
              u'注文日':'purchase_date',
              u'受注日':'purchase_date',# genesis order table
              u'受注番号':'order_code', # genesis order table & AcceptDetail. key for Merge
              u'売上時間':'purchase_time',
              u'売上時刻': 'purchase_time',
              u'会員カード番号':'user_id',
              u'生年月日':'birth_date',
              u'顧客コード':'user_code', # genesis customer table & order table
              u'ブランド':'brand',
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
              u'会員ランク':'user_rank',
              u'分類名':'category',
              u'商品コード':'itemcode',
              u'品番名':'item_code1',
              u'ショップコード':'shop_code',
              u'カテゴリーコード':'categorycode',
              u'カテゴリコード':'categorycode',
              u'【ecbeing】カテゴリコード':'categorycode',
              u'【genesis】商品分類1+2+3':'genesis',
              'S_DEPT':'SDEPT',
              u'商品分類1コード':'itemcode1',
              u'商品分類2コード':'itemcode2',
              u'商品分類3コード':'itemcode3',
              u'売上額':'price',
              u'POS販売時刻':'purchase_time',
              u'売上伝票番号':'slip_id',
              u'原価':'cost',
              u'ﾒｰｶｰｺｰﾄﾞ':'maker_code',
              u'ﾌﾞﾗﾝﾄﾞ':'brand',
              u'生年月':'birth_year_month',
              'DEPT':'DEPT',

              u'JANｺｰﾄﾞ':'jan_code'}

if __name__ == "__main__":
    iterm_master = pd.read_excel(path2+file5,dtype=col_dtype)
    iterm_master.rename(columns=colnamedic,inplace=True)
    iterm_master = iterm_master[['jan_code','DEPT','SDEPT','cost']]
    maker_code = pd.read_excel(path2+file6,dtype=col_dtype)
    maker_code.rename(columns=colnamedic,inplace=True)
    maker_code = maker_code[['maker_code','brand']]

    customers = pd.read_excel(path3+file7,dtype=col_dtype)
    customers.rename(columns=colnamedic,inplace=True)
    customers.birth_year_month = pd.to_datetime(customers.birth_year_month,format = '%Y/%m')
    customers.user_id = customers.user_id.astype(str)
    year = datetime.timedelta(days=365)
    customers.loc[:,'age'] = [(datetime.datetime(2017,1,1) - x)//year for x in customers.birth_year_month]
    col_list = list(set (customers.columns) & set(colnamedic.values()))
    customers = customers[col_list]
    customers = customers.set_index('user_id')

    pos = pd.read_excel(path1+file1,dtype=col_dtype)
    for fil in filelist[1:]:
        pos1 = pd.read_excel(path1 + fil, dtype=col_dtype)
        pos = pos.append(pos1)
    pos.rename(columns=colnamedic,inplace=True)
    pos.rename(columns=colnamedic_pos,inplace=True)

    print(pos.columns)
    print(iterm_master.columns)
    print(maker_code.columns)
    print(customers.columns)

    pos = pd.merge(pos,iterm_master , on ='jan_code')
    pos = pd.merge(pos,maker_code ,on ='maker_code')
    pos.purchase_date = pd.to_datetime(pos.purchase_date,format = '%Y%m%d')
    pos.purchase_time = pd.to_datetime(pos.purchase_time,format = '%H%M%S')
    pos.user_id = pos.user_id.astype(str)
    col_list = list(set(pos.columns) & set(colnamedic.values()))
    pos = pos[col_list]
    print(pos.columns)

    pos_jan = set(pos.jan_code)
    master_jan = set(iterm_master.jan_code)
    remain_jan = pos_jan-master_jan
    print("remain jans ="+str(len(remain_jan)))

    
    posold =  postable('unified').table
    userold =UserTable('cleanutable').usertable
    
    usernew = userold.append(customers)
    posold_cus = set(posold.user_id)
    user_old = set(userold.index)
    remain_old = list(posold_cus - user_old)
    pos_cus = set(pos.user_id)
    mas_cus = set(usernew.index)
    remain_cus = list(pos_cus-mas_cus)
    shop_codes = set(pos.shop)
    print ("shop codes = "+str(shop_codes))
    print ("pos cus = "+str(len(pos_cus)))
    print("pos old cus = "+str(len(posold_cus)))
    print ("old remain = "+str(len(remain_old)))
    print ("cus new table = "+str(len(customers.index)))
    print ("mas cus = "+str(len(mas_cus)))
    print("remaining customers ="+str(len(remain_cus)))
    for i in range(20):
        print ("customer = "+str(remain_cus[i]))
        print ("length of user_id is "+str(len(remain_cus[i])))


