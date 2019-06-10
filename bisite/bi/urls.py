from django.urls import path

from . import views

urlpatterns = [
    path('campaign/', views.campaign, name='campaign'),
    path('campaign/<int:campaign_id>/',views.campaigndetail,name='campaigndetail'),
    path('setup/',views.setup,name='setup'),
    path('setup/load_files/',views.setup_loadfiles,name='setup_load_files'),
#    path('setup/fetch_data/',views.setup_fetchdata,name='setup_fetch_data'),
#    path('setup/fetch_data_all/',views.setup_fetchdataall,name='setup_fetch_data'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('dashboard/result/',views.dashboard_result,name='dashboard_result'),
#    path('campaign/',views.campaigntop,name='campaign_top'),
#    path('campaign/edit/',views.campaign_edit,name='campaign_edit'),
    path('campaign/create/',views.campaign_create,name='campaign_create'),
    
]
