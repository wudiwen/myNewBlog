from django.conf.urls import url

from blog import views

app_name = 'blog'
urlpatterns = [
    url(r'^blog_index/', views.start_now, name='blog_index'),
    # path正向解析
    # path('blog_detail/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    # url正向解析
    url(r'^blog_detail/(?P<blog_id>\d+)/$', views.blog_detail, name='blog_detail'),
    url(r'^blog_detail/comment/(?P<post_id>\d+)/$', views.article_comment, name='article_comment'),
    url(r'^blog_detail/comment/(?P<post_id>\d+)/(?P<parent_comment_id>\d+)/$', views.article_comment,
        name='comment_reply'),
    url(r'^article_post/$', views.article_post, name='article_post'),
    url(r'^my_article/(?P<u_id>\d+)/', views.my_article, name='my_article'),
    url(r'^my_blog_detail/(?P<blog_id>\d+)/$', views.my_blog_detail, name='my_blog_detail'),
    url(r'^delete_article/(?P<a_id>\d+)/$', views.delete_article, name='delete_article'),
    url(r'^search/$', views.search, name='search'),
    url(r'^history/$', views.getHistory, name='history'),
    url(r'^del_history/(?P<blog_id>\d+)/$', views.del_history, name='del_history'),
    url(r'^collect/$', views.addCollect, name='collect'),
    url(r'^my_collect/$', views.my_collect, name='my_collect'),
    url(r'^cancelCol/(?P<blog_id>\d+)$', views.cancelCol, name='cancelCol'),

]
