from django.urls import path

from . import views

urlpatterns = [
    path('campaign/', views.campaign, name='campaign'),
    path('campaign/<int:campaign_id>/',views.campaigndetail,name='campaigndetail'),
    path('setup/',views.setup,name='setup'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('dashboard/result/',views.dashboard_result,name='dashboard_result'),
#    path('campaign/',views.campaigntop,name='campaign_top'),
#    path('campaign/edit/',views.campaign_edit,name='campaign_edit'),
    path('campaign/create/',views.campaign_create,name='campaign_create'),
    
]
