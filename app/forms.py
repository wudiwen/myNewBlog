from django import forms
from .models import User
from blog.models import ArticleComment, Article


# 创建评论表单
class CommentForm(forms.ModelForm):
    class Meta:
        model = ArticleComment
        fields = ['body']


# 创建发表博客的表单
class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['title', 'content']


# 上传头像表单
class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['nickname', 'icon']
