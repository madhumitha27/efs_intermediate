from django.conf.urls import url
from . import views
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

app_name = 'portfolio'
urlpatterns = [
    path('', views.home, name='home'),
    url(r'^home/$', views.home, name='home'),

    path('customer_list', views.customer_list, name='customer_list'),
    path('stock_list', views.stock_list, name='stock_list'),
    path('investment_list', views.investment_list, name='investment_list'),
    path ( 'register/' , views.register , name='register' ) ,
    path('customer/<int:pk>/edit/', views.customer_edit, name='customer_edit'),
    path('stock/<int:pk>/edit/', views.stock_edit, name='stock_edit'),
    path('investment/<int:pk>/edit/', views.investment_edit, name='investment_edit'),

    path('customer/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    path('stock/<int:pk>/delete/', views.stock_delete, name='stock_delete'),
    path('investment/<int:pk>/delete/', views.investment_delete, name='investment_delete'),

    path('stock/create/', views.stock_new, name='stock_new'),
    path('investment/create/', views.investment_new, name='investment_new'),

    path('customer/<int:pk>/portfolio/', views.portfolio, name='portfolio'),
    path('customer/<int:pk>/customerportfolio/', views.cust_portfolio, name='cust_portfolio'),
    path('customer/<int:pk>/download_portfolio/', views.download_portfolio, name='download_portfolio'),
path('customer/<int:pk>/sendemailpdf/', views.sendemailpdf, name='sendemailpdf'),

    url(r'^customers_json/', views.CustomerList.as_view()),
    path('customer/<int:pk>/', views.CustomerByNumber.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)
