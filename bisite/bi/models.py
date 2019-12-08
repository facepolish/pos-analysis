from django.db import models
from datetime import timedelta,datetime
from .dashboard import KojitsuPos
from django.contrib.auth import get_user_model


class ItemCategoryList (models.Model):
    upload = models.FileField(upload_to='uploads/%Y/%m/%d')
class ItemCategory (models.Model):
    dept = models.CharField(max_length=2)
    sdept = models.CharField(max_length=3)
    category_name = models.CharField(max_length=20)
    subcategory_name = models.CharField(max_length=20)
    def __str__(self):
        return (self.category_name+self.subcategory_name)

class SetUpData(models.Model):
    FILE_CHOICE = ((1,'店舗リスト'),(2,'顧客リスト'),(3,'POSデータ'),(4,'ECデータ'))
    datatype = models.PositiveSmallIntegerField(default=2,choices=FILE_CHOICE)
    upload = models.FileField(upload_to='uploads/%Y/%m/%d')
    def __str__(self):
        return(upload.path)

class UpListFile (models.Model):
    upload = models.FileField(upload_to='uploads/%Y/%m/%d')
    def __str__(self):
        return(upload.path)
'''
class CustomerList (models.Model):
    upload = models.FileField(upload_to='uploads/%Y/%m/%d')
    def __str__(self):
        return(upload.path)

class ShopList (models.Model):
    upload = models.FileField(upload_to='uploads/%Y/%m/%d')
    def __str__(self):
        return(upload.path)
'''

class Shops (models.Model):
    shop_code = models.CharField(max_length=3,unique=True)
    shop_name = models.CharField(max_length=100)
    def __str__(self):
        return(self.shop_name)

class Customer(models.Model):
    user_id = models.CharField(max_length=10,unique=True)
    address = models.CharField(max_length=200)
    gender = models.CharField(max_length=2)
    age = models.PositiveSmallIntegerField()
    age_group = models.PositiveSmallIntegerField()
    visit_count = models.PositiveSmallIntegerField()
    registered_date = models.DateField()
    user_rank = models.PositiveSmallIntegerField()
    def __str__(self):
        return self.user_id
    class Meta:
        permissions = (
            ("access_customer_data","Can access customer data"),
            ("update_customer_data","Can modify and update customer data")
        )
class Item(models.Model):
    DEPT = models.CharField(max_length=2,db_index=True)
    SDEPT = models.CharField(max_length=3,db_index=True)
    brand = models.CharField(max_length=100,db_index=True)
    type = models.CharField(max_length=100,db_index=True)
    item_name=models.CharField(max_length=200,db_index=True)
    def __str__(self):
        return self.item_name
class PosData(models.Model):
    shop = models.ForeignKey(Shops,on_delete=models.CASCADE,blank=True, null=True)
    user = models.ForeignKey(Customer,on_delete=models.CASCADE,blank=True, null=True)
    item = models.ForeignKey(Item,on_delete=models.CASCADE)
    purchase_datetime=models.DateTimeField()
    price = models.IntegerField()
    amount = models.SmallIntegerField()
    def __str__(self):
        return self.item.item_name
    class Meta:
        permissions = (
            ("access_pos_data","Can access pos data"),
            ("update_pos_data","can update pos data")
        )
class Campaign (models.Model):
    GRADE_CHOICE = ((1,'1合目登頂中'),(2,'4合目登頂中'),(3,'6合目登頂中'),(4,'8合目登頂中'),(5,'登頂達成！'))
    GENDER_CHOICE = (('男性','男性'),('女性','女性'))
    kp = KojitsuPos()
    pos = kp.GetPosTable()
    brandset = sorted(list(set(pos.brand)))
    BRAND_CHOICES = []
    for brand in brandset:
        BRAND_CHOICES.append((brand, brand))
    count_choice = [(i,i) for i in range(20)]
    count_term = [(0,'回以上'),(1,'回以下'),(3,'回ちょうど')]
    checkdateterms = [(1,'以降に購買あり'),(0,'以降に購買なし')]
    regionset = ['北海道','青森県','岩手県','宮城県','秋田県','山形県','福島県','茨城県','栃木県',
                '群馬県','埼玉県','千葉県','東京都','神奈川県','新潟県','富山県','石川県','福井県',
            '山梨県','長野県','岐阜県','静岡県','愛知県','三重県','滋賀県','京都府','大阪府','兵庫県',
            '奈良県','和歌山県','鳥取県','島根県','岡山県','広島県','山口県','徳島県','香川県','愛媛県',
            '高知県','福岡県','佐賀県','長崎県','熊本県','大分県','宮崎県','鹿児島県','沖縄県']
    REGION_CHOICES=[]
    for rg in regionset:
        REGION_CHOICES.append((rg, rg))
    DEPT_CHOICES = ((str(k),v) for k,v in kp.dept_dic.items())
    campaign_name = models.CharField(max_length=200)
    campaign_detail_text = models.TextField(max_length=400,null=True,blank=True)
    campaign_start_date = models.DateField(default=datetime.now, blank=True)
    campaign_end_date = models.DateField(default=datetime.now, blank=True)
    owner = models.ForeignKey(get_user_model(), verbose_name=u'オーナー', on_delete=models.CASCADE)

    UseAgeRange = models.BooleanField(default=False)
    agelower=models.PositiveSmallIntegerField(default=1)
    ageupper=models.PositiveSmallIntegerField(default=120)

    UseGender = models.BooleanField(default=False)
    gender=models.CharField(blank=True,max_length=2,choices=GENDER_CHOICE)

    UseGradeRange = models.BooleanField(default=False)
    gradelower=models.PositiveSmallIntegerField(default=1,choices=GRADE_CHOICE,blank=True)
    gradeupper=models.PositiveSmallIntegerField(default=5,choices=GRADE_CHOICE,blank=True)

    UseRegion = models.BooleanField(default=False)
    region=models.CharField(blank=True,max_length=20,choices=REGION_CHOICES)

    UseVisitCount = models.BooleanField(default=False)
    visitcount=models.PositiveSmallIntegerField(default=1,choices=count_choice,blank=True)
    visitcountterm=models.PositiveSmallIntegerField(default=1,choices=count_term,blank=True)
    
    UseRegisteredDate = models.BooleanField(default=False)
    regdatebegin = models.DateField(default=datetime.now,blank=True)
    regdateend = models.DateField(default=datetime.now,blank=True)

    UseLastPurchase = models.BooleanField(default=False)
    checkpointdate = models.DateField(default=datetime.now,blank=True)
    checkpointdateterm = models.PositiveSmallIntegerField(default=1,choices=checkdateterms,blank=True)

    UsePurchaseAddup = models.BooleanField(default=False)
    start_addup_date = models.DateField(null=True,blank=True)
    end_addup_date = models.DateField(null=True,blank=True)
    purchase_amount = models.PositiveIntegerField(default=0,blank=True)

    UseBrand = models.BooleanField(default=False)
    brand_name =models.CharField(blank=True,max_length=100,choices = BRAND_CHOICES)

    UseDEPT = models.BooleanField(default=False)
    DEPT_id =models.CharField(blank=True,max_length=2,choices = DEPT_CHOICES)

#    target_customers = models.ManyToManyField(Customer)
    def __str__(self):
        return self.campaign_name
    @property
    def customerlist(self):
        return self.target_customers.values_list('user_id',flat=True)
'''
        objlist = self.target_customers.all()
        customerlist=[]
        for user in objlist:
            customerlist.append(user.user_id)
        return customerlist
'''

class TargetShops (models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    shop_code = models.CharField(max_length=3,unique=True,blank=True)
# Create your models here.
