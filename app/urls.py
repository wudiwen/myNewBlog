from app import views
from django.conf.urls import url
from django.urls import path

app_name = 'account'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login, name='login'),
    url(r'^login_success$', views.login_success, name='login_success'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^register$', views.register, name='register'),
    url(r'^forget$', views.forget_password, name='forget'),
    url(r'^reset$', views.reset, name='reset'),

    url(r'^profile_edit/(?P<u_id>\d+)/$', views.profile_edit, name='profile_edit'),
    url(r'^upload/(?P<u_id>\d+)/$', views.upload, name='upload'),

]
