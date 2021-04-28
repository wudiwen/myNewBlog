from django.contrib import admin
from app.models import User
from blog.models import Article, ArticleComment, Category, Tag

# Register your models here.

# 添加自定义模型到admin管理界面
admin.site.register(User)
admin.site.register(Article)
admin.site.register(ArticleComment)
admin.site.register(Category)
admin.site.register(Tag)
