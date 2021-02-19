from django.contrib import admin
from django.conf.urls import  include,url
from django.urls import path,re_path
from django.contrib.auth import views
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, \
    PasswordResetConfirmView, PasswordResetCompleteView
from django.views.generic import TemplateView

urlpatterns = [

    re_path ( r'^accounts/login/$' , LoginView.as_view ( template_name='registration/login.html' ) , name="login" ) ,
    re_path ( r'^accounts/logout/$' , LogoutView.as_view ( template_name='registration/logout.html' ) ,
              LogoutView.next_page ,
              name="logout" ) ,
    path('admin/', admin.site.urls),
    path('', include('portfolio.urls')),
    re_path(r'^accounts/password/reset/$',
            PasswordResetView.as_view(template_name='registration/password_reset_page.html'), name='password_reset'),
    re_path(r'^accounts/password/reset/done/$',
            PasswordResetDoneView.as_view(template_name='registration/passwordreset_pagedone.html'),
            name='password_reset_done'),
    re_path(
        r'^accounts/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
        PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirmpage.html'),
        name='password_reset_confirm'),
    re_path(r'^accounts/password/reset/complete/$',
            PasswordResetCompleteView.as_view(template_name='registration/password_reset_completepage.html'),
            name='password_reset_complete'),

]
