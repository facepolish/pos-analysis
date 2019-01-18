import re
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Avg,Min,Max,Sum,F,FloatField
from .models import Campaign,Shops,Customer,UpListFile,PosData,Item
from .forms import DashBoardForm,CampaignCreateForm,SetupDataForm
import pandas as pd
from django.template import loader
from .dashboard import PosQueryGen,QueryUsersByTerm,PosQueryDiscount,PosQueryPriceTrend,ItemRelatedInfo,PosQuerySales,PosQueryWeeklyDetail
from datetime import datetime,timedelta
from pytz import timezone
import logging
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
import matplotlib

from django.contrib.auth.decorators import login_required,permission_required

@login_required
@permission_required("bi.access_pos_data")
def campaign_create(request):
    def RatioGraph(tabletpl,outputfile,title1,title2):
        font = {'family': 'IPAexGothic'}
        class numcol(object):
#            colors = list(matplotlib.colors.cnames.keys())
            colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
            c_count = len(colors)
            def __init__(self):
                self.count = 0
            def color(self):
                cn = self.count
                self.count = (cn+1)%numcol.c_count
                col = numcol.colors[cn]
                return(col)
        fig,ax = plt.subplots( 2, 1, figsize=(12,8), constrained_layout=True)
        fontp = font_manager.FontProperties(**font)
        plt.rcParams['font.family'] = 'IPAexGothic'
        ax[0].set_title(title1,**font)
        ax[0].set_xticklabels(tabletpl[0].columns,rotation='vertical',fontsize = 'small',**font)
        ax[1].set_xticklabels(tabletpl[1].columns,rotation='vertical',fontsize = 'small',**font)
        ax[1].set_title(title2,**font)
        nc = numcol()
        for ind,row in tabletpl[0].iterrows():
            ax[0].plot(tabletpl[0].columns,row,label=str(ind),color=nc.color())
        nc = numcol()
        for ind,row in tabletpl[1].iterrows():
            ax[1].plot(tabletpl[1].columns,row,label=str(ind),color=nc.color())
        ax[0].legend(prop=fontp)
        ax[1].legend(prop=fontp)
        fig.savefig(outputfile,format="png")
    
    if request.method == 'GET':
        template = loader.get_template('bi/campaign_create.html')
        context = {'form':CampaignCreateForm}
        return HttpResponse(template.render(context,request))
    elif request.method=='POST':
        form = CampaignCreateForm(request.POST)
        if not form.is_valid():
            raise ValueError('invalid form')
        name = form.cleaned_data['campaign_name']
        detail = form.cleaned_data['campaign_detail_text']
        s = form.cleaned_data['campaign_start_date']
        e = form.cleaned_data['campaign_end_date']
        campaign= Campaign.objects.create(campaign_name = name,campaign_detail_text=detail,campaign_start_date = s,campaign_end_date = e)
        qu = QueryUsersByTerm()
        userlist = qu.ExtractUsers(request.POST)
        chunksize=400
        lenlist = len(userlist)
        max_count = lenlist//chunksize +1
        for i in range(max_count):
            beg = chunksize*i
            upper = chunksize*(i+1)
            if upper>lenlist:
                upper = lenlist
            chunklist=userlist[beg:upper]
            cs = Customer.objects.filter(user_id__in=chunklist)
            campaign.target_customers.add(*cs)
        campaign.save()
        table,topratio,topbrand = PosQuerySales(userlist,(s-timedelta(days=365),s))
        fig,ax = plt.subplots( 2, 1, figsize=(12,8), constrained_layout=True)
        ax[0].plot(table.index,table.sales,label='Weekly Sales',color='b')
        ax[0].set_xticklabels(table.index,rotation='vertical',fontsize = 'small')
        ax[0].set_title('Weekly sales of Selected customers')
        ax[0].legend()
        ax[1].plot(table.index,table.ratio,label='Ratio',color='g')
        ax[1].set_xticklabels(table.index,rotation='vertical',fontsize = 'small')
        ax[1].set_title('Sales Share of Selected customers')
        ax[1].legend()
        fig.savefig('static/bi/chart2.png',format="png")
        
        RatioGraph(topratio,'static/bi/chart3.png','指定顧客種別売り上げ','指定顧客種別購入比率')
        RatioGraph(topbrand,'static/bi/chart4.png','指定顧客ブランド別売り上げ','指定顧客ブランド別購入比率')

        count =  campaign.target_customers.count()
        context = {'user_count':count}
        template = loader.get_template('bi/campaign_check.html')
        return HttpResponse(template.render(context,request))
        
@login_required    
@permission_required("bi.access_pos_data")
def campaign(request):
    if request.method=='POST':
        dellist = request.POST.getlist("delcampaign")
        for ob in dellist:
            Campaign.objects.filter(pk=ob).delete()
    latest_campaign_list = Campaign.objects.order_by('-campaign_start_date')[:5]
#    latest_campaign_list = Campaign.objects.order_by('-pk')[:5]
    template = loader.get_template('bi/campaign.html')
    context = {
        'latest_campaign_list': latest_campaign_list,
    }
    return HttpResponse(template.render(context,request))
    
@login_required
@permission_required("bi.access_pos_data")
def campaigndetail(request, campaign_id):
    try:
        campaign = Campaign.objects.get(pk=campaign_id)
        userlist = campaign.customerlist
        qt = QueryUsersByTerm()
    except Campaign.DoesNotExist:
        raise Http404("Campaign does not exist")
    if request.method == 'GET':
        table,per_cs,per_cs2 = qt.GenerateSummary(campaign.campaign_start_date,campaign.campaign_end_date,userlist)
        rowlisttop=['ブランド']
        rowlisttop.extend(table.columns)
        tablelist = [rowlisttop]
        for index,row in table.iterrows():
            rowlist = [index]
            rowlist.extend(row)
            tablelist.append(rowlist)
        summary_sheet = table.to_html()
        content = {'campaign': campaign,'table':tablelist}
        return render(request, 'bi/campaigndetail.html', content)
    elif request.method == 'POST':
        return render(request, 'bi/campaigndetail.html', {'campaign': campaign})

class progresscount(object):
    def __init__(self,table,init_mess,basic_mess,steps):
        self.max = table.shape[0]
        self.counter = 0
        self.initial_message = init_mess
        self.leg = self.max // steps
        self.accu = self.leg
        self.basic_mess = basic_mess
    def reset(self):
        self.counter = 0
    def check(self):
        if self.counter == 0:
            logging.debug(self.initial_message)
        self.counter += 1
        if self.counter > self.accu:
            logging.debug(self.basic_mess+'in progress '+str(self.counter)+' max = '+str(self.max))
            self.accu+=self.leg
            
@login_required        
@permission_required("bi.access_pos_data")
def setup(request):
    rename_dic = {'店舗ｺｰﾄﾞ':'shop_code','店名':'shop_name'}
    grade_dic = {'1合目登頂中':1,'4合目登頂中':2,'6合目登頂中':3,'8合目登頂中':4,'登頂達成！':5}
    col_dtype_new = {'user_id': str, 'user_rank': str,'purchase_time':str,'purchase_date':str}
    if request.method == 'GET':
        return render(request, 'bi/setup.html',{
            'form':SetupDataForm(),
        })
    elif request.method == 'POST':
#        form = SetupForm(request.POST,request.FILES)
        form = SetupDataForm(request.POST,request.FILES)
        if not form.is_valid():
            raise ValueError('invalid form')
        uplist = UpListFile()
        uplist.upload = form.cleaned_data['upload']
        uplist.save()
        if form.cleaned_data['datatype'] == 1:
               table = pd.read_csv(uplist.upload.path,encoding="cp932")
               table = table.rename(columns = rename_dic)
               for index, rw in table.iterrows():
                   try:
                       shop = Shops.objects.get(shop_code=rw.shop_code)
                       if shop.shop_name == rw.shop_name:
                           table=table.drop(index)
                           continue
                       else:
                           shop.shop_name = rw.shop_name
                   except Shops.DoesNotExist:
                       shop = Shops.objects.create(shop_code=rw.shop_code,shop_name=rw.shop_name)
                   shop.save()
               tablehttp = table.to_html()
               return HttpResponse(tablehttp)
        elif form.cleaned_data['datatype'] == 2:
               table = pd.read_csv(uplist.upload.path,encoding="cp932",dtype = col_dtype_new)
               table.registered_date = pd.to_datetime(table.registered_date,format='%Y%m')
               table.age = table.age.fillna(0)
               table.age_group = table.age_group.fillna(0)
               table.visit_count = table.visit_count.fillna(0)
               existing_users = Customer.objects.values_list('user_id',flat=True)
               remaining_users = set(table.user_id) - set(existing_users)
               table = table[table.user_id.isin(remaining_users)]
               bulk = []
               counter = progresscount(table,'Start Customer CSV validation','Customer DATA ',1000)
               for index, rw in table.iterrows():
                   counter.check()
                   try:
                       cs = Customer(user_id=rw.user_id,address=rw.address,
                           gender=rw.gender,age=rw.age,age_group=rw.age_group,visit_count=rw.visit_count,
                           registered_date=rw.registered_date,user_rank=grade_dic[rw.user_rank])
                       bulk.append(cs)
                    
                   except Customer.ValidationError:
                       logging.debug('Customer DATA has a validation error user_id = '+rw.user_id+' is ignored')
                       continue
                    
               Customer.objects.bulk_create(bulk)
               tablehttp = table.to_html()
               return HttpResponse(tablehttp)
        elif form.cleaned_data['datatype'] == 3:
            jp = timezone('Asia/Tokyo')
            table = pd.read_csv(uplist.upload.path,encoding="cp932",dtype = col_dtype_new)
            table.loc[:,'purchase_datetime'] = table.purchase_date+' '+table.purchase_time
            table.purchase_date = pd.to_datetime(table.purchase_date,format='%Y/%m/%d')
            table.purchase_time =  pd.to_datetime(table.purchase_time,format='%H%M%S')
            table.purchase_datetime =  pd.to_datetime(table.purchase_datetime,format='%Y/%m/%d %H%M%S').dt.tz_localize('Asia/Tokyo')
            table = table.sort_values('purchase_datetime')
            from_d = table.purchase_datetime[0]
            to_d = table.purchase_datetime[-1]
            posquery = PosData.objects.all()
            posd_term = posquery.aggregate(Min('purchase_datetime'),Max('purchase_datetime'))
            if not(posd_term['purchase_datetime__min'] is None):
                latestpos = table[table.purchase_datetime>posd_term['purchase_datetime__max']]
                pastpos = table[table.purchase_datetime<posd_term['purchase_datetime__min']]
                table = pastpos.append(latestpos)
            pc = progresscount(table,'Start POS CSV conversion','POS DATA ',10000)
            chunk_size = 1000
            row_count = table.shape[0]
            max_chunk = row_count//chunk_size
            cs_dic = {x.user_id:x for x in Customer.objects.all()}
            shop_dic = {x.shop_code:x for x in Shops.objects.all()}
            item_dic = {(x.DEPT,x.SDEPT,x.brand,x.type,x.item_name):x for x in Item.objects.all()}
            for n in range(max_chunk):
                chunk_begin = n*chunk_size
                chunk_end = (n+1)*chunk_size
                if chunk_end > row_count:
                    chunk_end = row_count
                chunk = table.iloc[chunk_begin:chunk_end,:]
                bulk = []
                for index,rw in chunk.iterrows():
                    pc.check()
                    item = item_dic.get((rw.DEPT,rw.SDEPT,rw.brand,rw.type,rw.item_name),None)
                    if item is None:
                        item = Item.objects.create(DEPT=rw.DEPT,SDEPT=rw.SDEPT,brand=rw.brand,
                            type=rw.type,item_name=rw.item_name)
                        item_dic.update({(rw.DEPT,rw.SDEPT,rw.brand,rw.type,rw.item_name):item})
                    us = cs_dic.get(rw.user_id,None)
                    sp = shop_dic.get(rw.shop,None)
                    ps = PosData(purchase_datetime=rw.purchase_datetime,
                        item=item,price=rw.price,amount=rw.amount,shop=sp,user=us)
                    bulk.append(ps)
                PosData.objects.bulk_create(bulk)

            res = pd.DataFrame(0,index = ['CSV Data','System Data'],columns = ['From','To'])
            res.loc['CSV Data','From'] = from_d
            res.loc['CSV Data','To'] = to_d
            res.loc['System Data','From'] = posd_term['purchase_datetime__min']
            res.loc['System Data','To'] = posd_term['purchase_datetime__max']
            tablehttp = res.to_html()
            return HttpResponse(tablehttp)


def GetTerm(request):
    beg = request.GET.get('begin_date',None)
    ed  = request.GET.get('end_date',None)
    if (beg is None) or (ed is None):
        ed = datetime.today()
        beg = ed - timedelta(weeks = 1)
        term = (beg,ed)
    else:
        beg = re.sub('[/.:]', '-', beg)
        ed = re.sub('[/.:]', '-', ed)
        beg = datetime.strptime(beg,'%Y-%m-%d')
        ed = datetime.strptime(ed,'%Y-%m-%d')
        if ed>beg:
            term=(beg,ed)
        else:
            term =(ed,beg)
    return(term)
def TermLocalize(term):
    jst = timezone('Asia/Tokyo')
    termret = (jst.localize(term[0]),jst.localize(term[1]))
    return(termret)
img_file = '../media/bi/img.png'

def highshareitems(table,share):
    table = table.sort_values(('price','sumprice'),ascending=False)
    limit_sumval = sum(table.price.sumprice)*share
    table.loc[:,'csum'] = table.price.sumprice.cumsum()
    table=table[table.csum<limit_sumval]
    return(table)

@login_required
@permission_required("bi.access_pos_data")
def dashboard_result(request):
    brand = request.GET.get('brand',None)
    shop_code = request.GET.get('shops',str(0))
    theme = request.GET.get('theme',0)
    itemid = request.GET.get('item',0)
    term = GetTerm(request)
    context = {}
    context['begin_date']=term[0]
    context['end_date']=term[1]
    context['shops'] = shop_code
    context['theme'] = theme
    context['item'] = itemid
    shop = int(shop_code)
    if shop == 0:
        shop_name = "全店舗"
    else:
        shop_name = Shops.objects.get(shop_code=shop).shop_name
    context['shop_name']=shop_name
    if theme == '0':
        context['brand'] = brand
        if brand is None:
            template = loader.get_template('bi/dashboardshop.html')
        else:
            template = loader.get_template('bi/dashboardbrand.html')
        toptable = PosQueryGen(term,shop_code,brand)
        tablelist = []
        for index,row in toptable.iterrows():
            rowlist = [index,row.ratio,int(row.previos_term),int(row.this_term)]
            tablelist.append(rowlist)
        context['toptable'] = tablelist
    elif theme == '1':
        template = loader.get_template('bi/dashboarddiscount.html')

        '''
        if shop == 0:
            q = Item.objects.all()
        else:
            q = Item.objects.filter(posdata__shop=shop_code)
        term = TermLocalize(term)
        q = q.filter(posdata__purchase_datetime__gte=term[0])
        q = q.filter(posdata__purchase_datetime__lte=term[1])
        agg = q.annotate(avg_price=Avg('posdata__price'),max_price=Max('posdata__price'))
#            discount_rate = Sum(F('posdata__price')/F('posdata__price'),output_field=FloatField()))
#        agg = agg.order_by('discount_rate')[:10]
        agg = agg[:10]
        
        tablelist = []
        for row in agg:
            rowlist = [row.item_name,row.avg_price,row.max_price
#                ,row.discount_rate
                       ]
            tablelist.append(rowlist)
        '''
        table = PosQueryDiscount(term,shop_code)
        table = table.sort_values(('price','sumprice'),ascending=False)
        table = highshareitems(table,0.5)
        tablelist = []
        for index,row in table.iterrows():
            rowlist = {'item':index,'category':row.item_category[0],'unit_avg':row.unit_price.avgprice,'unit_max':row.unit_price.maxprice,'discount':row.ratio,'sales':row.price.sumprice}
            tablelist.append(rowlist)
        context['toptable'] = tablelist
        
    elif theme == '2':
        template = loader.get_template('bi/dashboardpricetrend.html')
        table = PosQueryPriceTrend(term,itemid,shop_code)
        tablelist = []
        for index,row in table.iterrows():
            rowlist = [index,row.unit_price.avgprice,row.price.sumprice,row.unit_price.maxprice,row.unit_price.minprice]
            tablelist.append(rowlist)
        fig,ax = plt.subplots( 2, 1, figsize=(12,8), constrained_layout=True)
        ax[0].plot(table.index,table.unit_price.avgprice,label='Average Price',color='b')
        ax[0].plot(table.index,table.unit_price.maxprice,label='Weekly MAX Price',color='g')
        ax[0].plot(table.index,table.unit_price.minprice,label='Weekly MIN Price',color='y')
        ax[0].set_xticklabels(table.index,rotation='vertical',fontsize = 'small')
        ax[0].set_title('Weekly Average price')
        ax[0].legend()
        ax[1].plot(table.index,table.price.sumprice,label='Sales',color='g')
        ax[1].set_xticklabels(table.index,rotation='vertical',fontsize = 'small')
        ax[1].set_title('Weekly Sales')
        ax[1].legend()
        fig.savefig('static/bi/chart.png',format="png")
        context['toptable'] = tablelist
        iteminfo = ItemRelatedInfo(itemid)
        pricelist = iteminfo.netprices
        if len(pricelist)>0:
            context['netitem'] = pricelist
        wr = []
        for ind,row in iteminfo.cartrecommend.iterrows():
            wr.append({'brand':row.brand,'text':row.itemname,'category':row.category,'score':row.score})
        cr = []
        for ind,row in iteminfo.csrecommend.iterrows():
            cr.append({'brand':row.brand,'text':row.itemname,'category':row.category,'score':row.score})
        context['weeklyrecommend'] = wr
        context['userrecommend'] = cr
    elif theme == '3':
        template = loader.get_template('bi/dashboarditemweek.html')
        table = PosQueryWeeklyDetail(term,itemid,shop_code)
        tablelist = []
        for ind,row in table.iterrows():
            tablelist.append({'date':row.purchase_date,'time':row.purchase_time,'shop':Shops.objects.get(shop_code=row.shop).shop_name,'price':row.price,'amount':row.amount})
        context['toptable'] = tablelist
        

    return HttpResponse(template.render(context,request))

@login_required
@permission_required("bi.access_pos_data")
def dashboard(request):
    template = loader.get_template('bi/dashboardtop.html')
    context = {'form':DashBoardForm(),}
    return HttpResponse(template.render(context,request))
