from django import forms
from .models import Shops,Campaign,SetUpData



class CampaignCreateForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = '__all__'
        exclude = ['target_customers']
#        CAMPAIGNFORMLIST
        labels = {'campaign_name':"キャンペーン名",'campaign_detail_text':"キャンペーン詳細",'campaign_start_date':"開始日",'campaign_end_date':"終了日",
        'UseAgeRange':"年齢帯を使う",'UseGender':'性別を使う','UseGradeRange':'会員等級を使う',
        'UseRegion':'地域で絞る','UsePurchaseAddup':'期間購買金額で絞る',
        'UseBrand':'顧客ブランド親和性指標で絞る','UseCategory':'商品種別親和性指標で絞る','UseDEPT':'商品代分類で絞る'}
'''
        widgets = {
            'campaign_start_date': forms.SelectDateWidget(years=[x for x in range(1990, 2030)]),
            'campaign_end_date': forms.SelectDateWidget(years=[x for x in range(1990, 2030)]),
            'start_addup_date': forms.SelectDateWidget(years=[x for x in range(1990, 2030)]),
            'end_addup_date': forms.SelectDateWidget(years=[x for x in range(1990, 2030)]),
            'start_brandtest_date': forms.SelectDateWidget(years=[x for x in range(1990, 2030)]),
            'end_brandtest_date': forms.SelectDateWidget(years=[x for x in range(1990, 2030)]),
        }
'''

class SetupDataForm(forms.ModelForm):
    class Meta:
        model = SetUpData
        fields = '__all__'
        labels = {'datatype':"アップロードファイル種別",'upload':"ファイル:"}
'''
class SetupForm(forms.Form):
    upload = forms.FileField()
'''
    
class DashBoardForm(forms.Form):
    shopobj = Shops.objects.all()
    shop_choices = [('0','全店舗')]
    theme_choices = [(0,'ブランド分析'),(1,'商品売り上げ順'),(10,'直近来店')]
    for shop in shopobj:
        shop_choices.append((shop.shop_code,shop.shop_name))
    shops = forms.ChoiceField(
        label = '対象店舗',
        required = True,
        widget = forms.Select,
        choices = shop_choices)
    begin_date = forms.DateField(
        label = '開始日',
        required=True,
        input_formats=[
            '%Y-%m-%d',
            '%Y/%m/%d'
        ])
    end_date = forms.DateField(
        label = '終了日',
        required=True,
        input_formats=[
            '%Y-%m-%d',
            '%Y/%m/%d'
        ])
    theme = forms.ChoiceField(
        label = '集計項目',
        required=True,
        widget = forms.Select,
        choices = theme_choices)
    
