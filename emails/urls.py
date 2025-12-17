from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('campaigns/', views.campaign_list, name='campaign_list'),
    path('campaigns/<int:pk>/', views.campaign_detail, name='campaign_detail'),
    path('campaigns/create/', views.create_campaign, name='create_campaign'),
    path('campaigns/<int:pk>/send/', views.send_campaign, name='send_campaign'),
    path('recipients/add/', views.add_recipient, name='add_recipient'),
    path('track/open/<uuid:tracking_id>/', views.track_open, name='track_open'),
    path('track/click/<uuid:tracking_id>/', views.track_click, name='track_click'),
]