import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from sklearn.decomposition import NMF
import os
import pickle
import numba
import datetime as dt
from django.conf import settings
from scipy.sparse import csr_matrix
from pandas.api.types import CategoricalDtype
from .tableclass import postable, UserTable, DEPTtable
from .kakakucom import GetPricefromKakaku
from .createitemvec import ItemRecommend

gradedic = {'1合目登頂中': 1, '4合目登頂中': 2, '6合目登頂中': 3, '8合目登頂中': 4, '登頂達成！': 5}
posfile = os.path.join(settings.BASE_DIR, 'bi/data/bi/pos.pkl')
userfile = os.path.join(settings.BASE_DIR, 'bi/data/bi/user.pkl')
uservecfile = os.path.join(settings.BASE_DIR, 'bi/data/bi/uservec.pkl')
itemvecfile = os.path.join(settings.BASE_DIR, 'bi/data/bi/itemvec.pkl')
itemiddicfile = os.path.join(settings.BASE_DIR, 'bi/data/bi/itemid.pkl')
depttablefile = os.path.join(settings.BASE_DIR, 'bi/data/bi/dept.pkl')
sdepttablefile = os.path.join(settings.BASE_DIR, 'bi/data/bi/sdept.pkl')


def PivotSum(table):
    table.loc[:, 'count'] = 1
    try:
        userbyitem = pd.pivot_table(table, index='user_id', columns='itemid', values='count', aggfunc='sum')
        userbyitem = userbyitem.fillna(0)
        return (userbyitem)
    except:
        person_c = CategoricalDtype(sorted(table.user_id.unique()), ordered=True)
        thing_c = CategoricalDtype(sorted(table.itemid.unique()), ordered=True)
        row = table.user_id.astype(person_c).cat.codes
        col = table.itemid.astype(thing_c).cat.codes
        sparse_matrix = csr_matrix((table['count'], (row, col)),
                                   shape=(person_c.categories.size, thing_c.categories.size))
        dfs = pd.SparseDataFrame(sparse_matrix, index=person_c.categories, columns=thing_c.categories,
                                 default_fill_value=0)
        return (dfs)


def UserItemVec(pos1, user1):
    userbyitem = PivotSum(pos1)
    #    userbyitem[userbyitem<0]=0
    model = NMF(n_components=10, init='random', random_state=0, solver='mu')
    #    testframe = userbyitem.iloc[0:userbyitem.shape[0]//2,:]
    #    P = model.fit_transform(testframe)

    P = model.fit_transform(userbyitem)
    Q = model.components_
    user_vec = pd.DataFrame(P, index=userbybrand.index)
    user_vec = user_vec[user_vec.index.isin(user1.index)]
    item_vec = pd.DataFrame(Q.T, index=userbyitem.columns)
    return (user_vec, item_vec)


class KojitsuPos(object):
    __posupdated = False
    __userupdated = False
    if os.path.exists(posfile):
        postable = pd.read_pickle(posfile)
    else:
        postable = postable('unified').table
        postable.loc[:, 'itemid'] = postable.brand + postable.type + postable.item_name
        postable.loc[:, 'unit_price'] = postable.price / postable.amount
        weeks = [str(x.isocalendar()[0]) + ' ' + str(x.isocalendar()[1]).rjust(2) for x in postable.purchase_date]
        lenw = len(weeks)
        lenpos = postable.shape[0]
        postable.loc[:, 'year_week'] = weeks
        postable.to_pickle(posfile)
        __posupdated = True
    if os.path.exists(userfile):
        usertable = pd.read_pickle(userfile)
    else:
        usertable = UserTable('cleanutable').usertable
        usertable.user_rank = usertable.user_rank.replace(gradedic)
        usertable.to_pickle(userfile)
        __userupdated = True
    '''
    if (not (__posupdated or __userupdated)) and (os.path.exists(itemvecfile) and os.path.exists(uservecfile)):
        item_vec=pd.read_pickle(itemvecfile)
        user_vec=pd.read_pickle(uservecfile)
    else:
        user_vec,item_vec = UserItemVec(postable,usertable)
        item_vec.to_pickle(itemvecfile)
        user_vec.to_pickle(uservecfile)
    '''
    if os.path.exists(depttablefile):
        with open(depttablefile, 'rb') as f:
            deptsdept_dic = pickle.load(f)
    else:
        dpt = DEPTtable('HITRMD_DEPT')
        dept_dic = dpt.namedic
        sdept_dic = dpt.subdic
        deptsdept_dic = {}
        for k,v in dept_dic.items():
            sdic = sdept_dic[k]
            for sk,sv in sdic.items():
                deptsdept_dic.update({(k,sk):v+' '+sv})
        with open(depttablefile, 'wb') as f:
            pickle.dump(deptsdept_dic, f)

    if os.path.exists(itemiddicfile):
        with open(itemiddicfile, 'rb') as f:
            itemid_dic = pickle.load(f)
    else:
        itemid_dic = {id: {'brand':b,'type': t,'name': n,'DEPT_SDEPT':(d, s)} for id, b, t, n, d, s in
                      zip(postable.itemid, postable.brand, postable.type, postable.item_name, postable.DEPT,
                          postable.SDEPT)}
        with open(itemiddicfile, 'wb') as f:
            pickle.dump(itemid_dic, f)

    #    def __init__(self):
    #        self.postable = self.postable
    @classmethod
    def GetPosTable(cls):
        return (cls.postable)

    @classmethod
    def GetUserTable(cls):
        return (cls.usertable)

    @classmethod
    def GetItemVec(cls):
        return (cls.item_vec)

    @classmethod
    def GetItemData(cls, id):
        item = cls.itemid_dic.get(id, None)
        if item is None:
            return(None)
        return (item)
    @classmethod
    def GetCategory(cls,itemid):
        item = cls.itemid_dic[itemid]
        deptsdept = item['DEPT_SDEPT']
        ret_str = cls.deptsdept_dic[deptsdept]
        return(ret_str)


def PrevTerm(term):
    dys = term[1] - term[0]
    prevend = term[0] - dt.timedelta(days=1)
    prevbeg = prevend - dys
    return ((prevbeg, prevend))


def ActualyMax(list):
    #    s = list.sort_values(ascending=False)
    s = sorted(list, reverse=True)
    l = len(s)
    if l > 2:
        val = s[1]
    else:
        val = s[0]
    return (val)


def PosQueryPriceTrend(term, item, shop=None):
    tb = KojitsuPos()
    pos = tb.GetPosTable()
    if (shop == '0') or (shop is None) or (shop == 'all'):
        tpos = pos
    else:
        tpos = pos[pos.shop == int(shop)]
    tpos = tpos[tpos.purchase_date >= term[0]]
    tpos = tpos[tpos.purchase_date <= term[1]]

    tpos = tpos[tpos.itemid == item]
    tpos = tpos[['price', 'year_week', 'unit_price']]
    pricetrend = tpos.groupby('year_week').agg({'price': 'sum', 'unit_price': ['mean', 'max', 'min']})
    pricetrend = pricetrend.rename(
        columns={'sum': 'sumprice', 'max': 'maxprice', 'mean': 'avgprice', 'min': 'minprice'})
    pricetrend.index = [dt.datetime.strptime(x + ' 1', '%G %V %u').strftime('%Y/%m/%d') for x in pricetrend.index]
    return (pricetrend)


def PosQueryDiscount(term, shop=None):
    tb = KojitsuPos()
    pos = tb.GetPosTable()
    if (shop == '0') or (shop is None) or (shop == 'all'):
        tpos = pos
    else:
        tpos = pos[pos.shop == int(shop)]
    tpos = tpos[tpos.purchase_date >= term[0]]
    tpos = tpos[tpos.purchase_date <= term[1]]
    tpos = tpos[['price', 'itemid', 'unit_price']]
    sumpos = tpos.groupby('itemid').agg({'price': 'sum', 'unit_price': ['max', 'min', 'mean']})
    sumpos = sumpos.rename(columns={'sum': 'sumprice', 'max': 'maxprice', 'mean': 'avgprice', 'min': 'minprice'})
    sumpos.loc[:, 'ratio'] = sumpos.unit_price.avgprice / sumpos.unit_price.maxprice
    sumpos.loc[:, 'item_category'] = [tb.GetCategory(x) for x in sumpos.index]
    return (sumpos)

    minpos = tpos.groupby


def PosQueryGen(term, shop=None, brand_id=None):
    def InTerm(table, term):
        table1 = table[table.purchase_date >= term[0]]
        table1 = table1[table1.purchase_date <= term[1]]
        return (table1)

    tb = KojitsuPos()
    pos = tb.GetPosTable()
    if (shop == '0') or (shop is None) or (shop == 'all'):
        tpos = pos
    else:
        tpos = pos[pos.shop == int(shop)]
    if not (brand_id is None):
        tpos = tpos[tpos.brand == brand_id]
        target_col = 'item_name'
    else:
        target_col = 'brand'

    prev_term = PrevTerm(term)
    termpos = InTerm(tpos, term)
    prevpos = InTerm(tpos, prev_term)

    termpos = termpos[[target_col, 'price']]
    prevpos = prevpos[[target_col, 'price']]

    totalsaleterm = sum(termpos.price)
    totalsaleprev = sum(prevpos.price)

    brand1 = termpos.groupby(target_col).sum()
    brand1.loc[:, 'share'] = brand1.price / float(totalsaleterm)

    brand2 = prevpos.groupby(target_col).sum()
    brand2.loc[:, 'share'] = brand2.price / float(totalsaleprev)
    brand1 = brand1.assign(ratio=0)
    brand1 = brand1.assign(previos_term=0)

    for index, row in brand1.iterrows():
        if index in brand2.index:
            brand1.loc[index, 'ratio'] = brand1.loc[index, 'share'] / brand2.loc[index, 'share']
            brand1.loc[index, 'previos_term'] = brand2.loc[index, 'price']
        else:
            brand1.loc[index, 'ratio'] = 100
            brand1.loc[index, 'previos_term'] = 0
    brand1 = brand1.sort_values(by=['ratio'], ascending=False)
    brand1 = brand1.rename(columns={'price': 'this_term'})
    return (brand1)


def PosQuery():
    term = (dt.date(2017, 8, 1), dt.date(2017, 8, 7))
    table = PosQueryGen(term)
    table = table[table.this_term > 1000000]
    return (table)


def PosQueryBrand(brand_id):
    term = (dt.date(2017, 8, 1), dt.date(2017, 8, 7))
    return (PosQueryGen(term, None, brand_id))


def QueryUsers(terms):
    tb = KojitsuPos()
    pos = tb.GetTable()
    return (pos.shape[0])


class QueryUsersByTerm(object):
    def grade(self, user, para):
        user1 = user
        low = min(int(para[0]), int(para[1]))
        high = max(int(para[0]), int(para[1]))
        user2 = user1[user1.user_rank >= low]
        user2 = user2[user2.user_rank <= high]
        return (user2)

    def region(self, user, para):
        user1 = user
        reg = para[0]
        leng = len(reg)
        user2 = user1[user1.address[:leng] == reg]
        return (user2)

    def Addup(self, user, param):
        user1 = user
        pos = self.pos
        pos1 = pos[pos.user_id.isin(user1.index)]
        day1 = dt.datetime.strptime(param[0], '%Y-%m-%d')
        day2 = dt.datetime.strptime(param[1], '%Y-%m-%d')
        low = min(day1, day2)
        high = max(day1, day2)
        pos1 = pos1[pos1.purchase_date >= low]
        pos1 = pos1[pos1.purchase_date <= high]
        pos1 = pos1[['user_id', 'price']]
        agg = pos1.groupby('user_id').sum()
        agg = agg[agg.price >= int(param[2])]
        user2 = user1[user1.index.isin(agg.index)]
        return (user2)

    def brandvecmetric(self, user, param):
        user1 = user
        pos = self.pos
        brand = param[0]
        maxcount = int(param[3])
        day1 = dt.datetime.strptime(param[1], '%Y-%m-%d')
        day2 = dt.datetime.strptime(param[2], '%Y-%m-%d')
        low = min(day1, day2)
        high = max(day1, day2)
        pos1 = pos[pos.purchase_date >= low]
        pos1 = pos1[pos1.purchase_date <= high]
        userbybrand = pd.pivot_table(pos1, index='user_id', columns='brand', values='price', aggfunc='sum').fillna(0)
        userbybrand[userbybrand < 0] = 0
        model = NMF(n_components=10, init='random', random_state=0)
        P = model.fit_transform(userbybrand)
        Q = model.components_
        if brand not in userbybrand.columns:
            return (user1)
        user_vec = pd.DataFrame(P, index=userbybrand.index)
        user_vec = user_vec[user_vec.index.isin(user1.index)]
        brand_vec = pd.DataFrame(Q.T, index=userbybrand.columns)
        user_metric = user_vec.dot(brand_vec.loc[brand, :].T)
        user_metric = user_metric.sort_values(ascending=False)
        if user_metric.shape[0] > maxcount:
            tpos = user_metric.index[0:maxcount]
        else:
            tpos = user_metric.index
        user2 = user1[user1.index.isin(tpos)]
        return (user2)

    def gender(self, user, para):
        user1 = user
        gen = para[0]
        user2 = user1[user1.gender == gen]
        return (user2)

    def age(self, user, para):
        # para 0 -> usertable, para 1 -> user agerange
        if (user is None):
            user1 = self.user
        else:
            user1 = user
        low = min(int(para[0]), int(para[1]))
        high = max(int(para[0]), int(para[1]))
        user2 = user1[user1.age >= low]
        user2 = user2[user2.age <= high]
        return (user2)

    factors = {'UseAgeRange': (('agelower', 'ageupper'), age),
               'UseGender': (('gender',), gender),
               'UseGradeRange': (('gradelower', 'gradeupper'), grade),
               'UseRegion': (('region',), region),
               'UsePurchaseAddup': (('start_addup_date', 'end_addup_date', 'purchase_amount'), Addup),
               'UseBrand': (
               ('brand_name', 'start_brandtest_date', 'end_brandtest_date', 'brand_user_max'), brandvecmetric)
               #    ('UseCategory',('category_id','start_categorytest_date','end_categorytest_date'),self.)
               }

    def __init__(self):
        kp = KojitsuPos()
        self.pos = kp.GetPosTable()
        self.user = kp.GetUserTable()

    def formlist(self):
        nulist = []
        for k, v in self.factors.items():
            nulist.append(k)
            for pa in v[0]:
                nulist.append(pa)
        return (nulist)

    def ExtractUsers(self, POST):
        user = self.user
        for k, v in self.factors.items():
            if POST.get(k, False):
                tp = ()
                params = v[0]
                func = v[1]
                for para in params:
                    tp += (POST[para],)
                user = func(self, user, tp)
        return (user.index)

    def GenerateSummary(self, date1, date2, userlist):
        datelow = min(date1, date2)
        datehigh = max(date1, date2)
        pos1 = self.pos
        pos1 = pos1[pos1.purchase_date >= datelow]
        pos1 = pos1[pos1.purchase_date <= datehigh]
        pos2 = pos1
        pos1 = pos1[pos1.user_id.isin(userlist)]

        table, persales1, persales2 = TendencyAna(pos1, pos2)
        return (table, persales1, persales2)


def TendencyAna(pos1, pos2):
    def persale(sale, count):
        if count == 0:
            return (0)
        else:
            return (sale / float(count))

    rendic = {'price': '対象顧客総額', 'price2': '全体総額', 'ratio1': '対象客比率', 'ratio2': '全体比率', 'ratio3': '比率比(対象/全体)'}
    count1 = len(set(pos1.user_id))
    count2 = len(set(pos2.user_id))

    gr1 = pos1[['brand', 'price']]
    gr2 = pos2[['brand', 'price']]
    gr1 = gr1.groupby('brand').sum()
    gr2 = gr2.groupby('brand').sum()
    sum1 = sum(gr1.price)
    sum2 = sum(gr2.price)

    gr1.loc[:, 'ratio1'] = gr1.price / float(sum1)
    gr2.loc[:, 'ratio2'] = gr2.price / float(sum2)
    gr2 = gr2.rename(columns={'price': 'price2'})
    gr1 = gr1.join(gr2)
    gr1.loc[:, 'ratio3'] = gr1.ratio1 / gr1.ratio2
    gr1 = gr1.sort_values(by='ratio3', ascending=False)
    gr1 = gr1.rename(columns=rendic)
    return (gr1, persale(sum1, count1), persale(sum2, count2))


class ItemRelatedInfo(object):
    def __init__(self, itemid):
        self.itemid = itemid
        tp = KojitsuPos()
        item = tp.GetItemData(itemid)
        self.brand = item['brand']
        self.itemname = item['name']
        self.netprices = GetPricefromKakaku(self.brand, self.itemname)
        itemrec = ItemRecommend()
        cartrec = itemrec.getsamecartrecommendlist(itemid)
        self.cartrecommend = cartrec.iloc[1:11, :]
        self.cartrecommend.loc[:, 'brand'] = [tp.GetItemData(x)['brand'] for x in self.cartrecommend.index]
        self.cartrecommend.loc[:, 'itemname'] = [tp.GetItemData(x)['name'] for x in self.cartrecommend.index]
        csrec = itemrec.getsamecustomerrecommendlist(itemid)
        self.csrecommend = csrec.iloc[1:11, :]
        self.csrecommend.loc[:, 'brand'] = [tp.GetItemData(x)['brand'] for x in self.csrecommend.index]
        self.csrecommend.loc[:, 'itemname'] = [tp.GetItemData(x)['name'] for x in self.csrecommend.index]
