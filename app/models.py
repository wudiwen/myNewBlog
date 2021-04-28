from django.db import models
from django.contrib import admin
from django.urls import reverse
from django.utils.timezone import now

from django.core.exceptions import ObjectDoesNotExist


# Create your models here.


# 创造用户表

class User(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=200)
    nickname = models.CharField(max_length=50)
    email = models.EmailField()
    created_time = models.CharField(max_length=50, default=now)
    comment_num = models.PositiveIntegerField(verbose_name='评论数', default=0)
    icon = models.ImageField(upload_to='media', default='media/default.png')

    def __str__(self):
        return self.username

    def comment(self):
        self.comment_num += 1
        # 只要用户发起评论，更新该用户的评论数量
        self.save(update_fields=['comment_num'])

    def comment_del(self):
        self.comment_num -= 1
        self.save(update_fields=['comment_num'])


# 收藏表
class Collect(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collected_article')
    article = models.ForeignKey('blog.Article', on_delete=models.CASCADE, related_name='collected_user')

    def __str__(self):
        try:
            return self.article.title
        except:
            return 'not collect'


# 管理员用户
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
