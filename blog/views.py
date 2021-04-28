from django.core.paginator import Paginator
from django.core.cache import cache
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django_redis import get_redis_connection
from django.db.models import Q
from django.views.decorators.clickjacking import xframe_options_exempt, xframe_options_sameorigin
from django.views.decorators.cache import cache_page

from app.models import User, Collect
from app.views import check_user
from blog.models import Article, Category, ArticleComment, Tag
from app.forms import CommentForm, ArticleForm


# Create your views here.


# 进入博客首页
# @cache_page(60*15)
def start_now(request):
    if request.GET.get('action') == 'views':
        blogs = Article.objects.all().order_by('-views')
        action = 'views'
    else:
        blogs = Article.objects.all().order_by('-created_time')
        action = 'normal'
    paginator = Paginator(blogs, 3)  # 每页5条数据
    page = request.GET.get('page', 1)  # 默认跳转到第一页
    result = paginator.page(page)
    state = request.session.get('IS_LOGIN', '')
    if state:
        u_id = request.session.get('id', '')
        user = User.objects.get(id=u_id)
        return render(request, 'blog/blog_index.html',
                      {"blogs": result, 'state': state, 'user': user, 'action': action})
    else:
        return render(request, 'blog/blog_index.html', {"blogs": result, 'state': state, 'action': action})


# 博客详情
@check_user
def blog_detail(request, blog_id):
    u_id = request.session.get('id', '')
    user = User.objects.get(id=u_id)
    blog = Article.objects.get(id=blog_id)
    # 更改浏览量
    blog.viewed()

    # 添加浏览记录
    connect = get_redis_connection('default')
    history_key = 'history_%d' % (u_id)
    # 移除相同的记录
    connect.lrem(history_key, 0, blog_id)
    # 从左侧添加记录
    connect.lpush(history_key, blog_id)
    # 保留最新的10个记录
    connect.ltrim(history_key, 0, 9)
    form = CommentForm()
    comment_list = blog.articlecomment_set.all()
    # 获取该用户的所有收藏博客
    collect_list = user.collected_article.all()
    # 清除缓存
    cache.delete('history_data')

    collect_id = []
    has_fav = 0
    for x in collect_list:
        collect_id.append(str(x.article_id))
    # print(type(blog_id))
    if blog_id in collect_id:
        has_fav = 1
    # print(has_fav)
    context = {
        'article': blog,
        'form': form,
        'comment_list': comment_list,
        'has_fav': has_fav,
    }
    return render(request, 'blog/blog_detail.html', context=context)


'''
# 一级评论
@check_user
def article_comment(request, post_id):
    # 这个函数的作用是当获取的文章（Article）存在时，则获取；否则返回 404 页面给用户。
    article = get_object_or_404(Article, id=post_id)
    u_id = request.session.get('id', '')
    if request.method == 'POST':
        form = CommentForm(request.POST)

        # 当调用 form.is_valid() 方法时，Django 自动帮我们检查表单的数据是否符合格式要求。
        if form.is_valid():
            # 检查到数据是合法的，调用表单的 save 方法保存数据到数据库，
            # commit=False 的作用是仅仅利用表单的数据生成 Comment 模型类的实例，但还不保存评论数据到数据库。
            new_comment = form.save(commit=False)
            new_comment.article = article
            # new_comment.user = request.user
            new_comment.user = User.objects.get(id=u_id)
            new_comment.save()
            new_comment.user.comment()
            return redirect('/blog/blog_detail/{}/'.format(article.id))
        else:
            #  article.articlecomment_set.all() 方法，
            # 这个用法有点类似于 Article.objects.all()
            # 获取全部评论
            comment_list = article.articlecomment_set.all()
            context = {
                'article': article,
                'form': form,
                'comment_list': comment_list,
            }
            return render(request, 'blog/blog_detail.html', context=context)
    else:

        return redirect(article)  # 返回详情页
'''


# 多级评论
@check_user
# @xframe_options_exempt  # 无限制
@xframe_options_sameorigin  # 同一域名下可以嵌套网页
def article_comment(request, post_id, parent_comment_id=None):
    # 这个函数的作用是当获取的文章（Article）存在时，则获取；否则返回 404 页面给用户。
    article = get_object_or_404(Article, id=post_id)
    u_id = request.session.get('id', '')
    if request.method == 'POST':
        form = CommentForm(request.POST)

        # 当调用 form.is_valid() 方法时，Django 自动帮我们检查表单的数据是否符合格式要求。
        if form.is_valid():
            # 检查到数据是合法的，调用表单的 save 方法保存数据到数据库，
            # commit=False 的作用是仅仅利用表单的数据生成 Comment 模型类的实例，但还不保存评论数据到数据库。
            new_comment = form.save(commit=False)
            new_comment.article = article
            # new_comment.user = request.user
            new_comment.user = User.objects.get(id=u_id)
            new_comment.nickname = new_comment.user.nickname

            # 二级回复
            if parent_comment_id:
                print(parent_comment_id)
                parent_comment = ArticleComment.objects.get(id=parent_comment_id)
                # 如果回复层级超过二层，强制转化成二级
                new_comment.parent_id = parent_comment.get_root().id
                # 被回复的人
                new_comment.reply_to = parent_comment.user
                new_comment.nickname = User.objects.get(id=u_id).nickname
                new_comment.save()
                return HttpResponse('200 OK')

            new_comment.save()
            return redirect('/blog/blog_detail/{}/'.format(article.id))
        else:
            return HttpResponse('提交表单有问题')
    elif request.method == 'GET':
        form = CommentForm()
        comment_list = article.articlecomment_set.all()
        context = {
            'article_id': post_id,
            'form': form,
            'parent_comment_id': parent_comment_id,
        }
        print('12232321231321321')
        return render(request, 'blog/reply.html', context=context)
        # return HttpResponse('回复界面')


# 发表博客
@check_user
def article_post(request):
    u_id = request.session.get('id', '')
    user = User.objects.get(id=u_id)
    if request.method == 'POST':
        article_post_form = ArticleForm(data=request.POST)
        if article_post_form.is_valid():
            print('==================')
            cd = article_post_form.cleaned_data
            new_article = article_post_form.save(commit=False)
            new_article.author = User.objects.get(id=u_id)
            # print(request.user.id)
            # 获取下拉框选择的分类id
            cate = request.POST['c_category']
            # print(cate)
            new_article.category = Category.objects.get(id=cate)
            new_article.save()
            return redirect(reverse('blog:blog_index'))
    else:
        article_post_form = ArticleForm()
        # cate = Category.objects.all()
        # print(cate)
        article_categorys = Category.objects.all()
        print('=======', article_categorys)
        return render(request, 'blog/article_post.html',
                      {'article_post_form': article_post_form, 'article_categorys': article_categorys, 'user': user})


# 我的博客列表
@check_user
def my_article(request, u_id):
    user_id = request.session.get('id', '')
    user = User.objects.get(id=u_id)
    article_list = user.article_set.all()
    paginator = Paginator(article_list, 3)  # 每页3条数据
    page = request.GET.get('page', 1)  # 默认跳转到第一页
    article_list = paginator.page(page)
    if str(user_id) == str(u_id):
        return render(request, 'blog/my_article.html', {'article_list': article_list, 'user': user})
    else:
        return render(request, 'blog/other_article.html', {'article_list': article_list, 'user': user})


# 我的博客中的文章详情
@check_user
def my_blog_detail(request, blog_id):
    blog = Article.objects.get(id=blog_id)
    # 更改浏览量
    blog.viewed()
    form = CommentForm()
    comment_list = blog.articlecomment_set.all()
    context = {
        'article': blog,
        'form': form,
        'comment_list': comment_list,
    }
    return render(request, 'blog/my_blog_detailed.html', context=context)


# 删除博客
@check_user
def delete_article(request, a_id):
    u_id = request.session.get('id', '')
    article = Article.objects.get(id=a_id)
    article.delete()
    return redirect('/blog/my_article/{}/'.format(u_id))


# 搜索博客
def search(request):
    q = request.GET.get('q', '')
    content = Article.objects.all()
    search_list = Article.objects.filter(
        Q(title__contains=q) | Q(author__username__contains=q) | Q(content__contains=q))
    print(search_list)
    msg = '没有结果'
    return render(request, 'blog/search.html', {'content': content, 'search_list': search_list, 'msg': msg})


# 获取浏览记录
@check_user
def getHistory(request):
    # 尝试从缓存中获取数据
    content = cache.get('history_data')
    print('从缓存获取的数据')
    if content is None:
        print('从数据库中获取的数据')
        u_id = request.session.get('id', '')
        user = User.objects.get(id=u_id)
        connect = get_redis_connection('default')
        history_key = 'history_%d' % (u_id)
        # 获取最新的10个记录
        blog_ids = connect.lrange(history_key, 0, 9)
        all_blogs = []
        for blog_id in blog_ids:
            blogs = Article.objects.get(id=blog_id)
            all_blogs.append(blogs)

        content = {
            'all_blogs': all_blogs,
            'user': user
        }

        # 设置缓存
        cache.set('history_data', content, 60 * 60)
    return render(request, 'blog/history.html', content)


@check_user
# 删除浏览记录
def del_history(request, blog_id):
    u_id = request.session.get('id', '')
    user = User.objects.get(id=u_id)
    # 清除缓存
    cache.delete('history_data')
    connect = get_redis_connection('default')
    history_key = 'history_%d' % (u_id)
    # 删除记录
    connect.lrem(history_key, 0, blog_id)

    return redirect('blog:history')


# 添加/取消 收藏
@check_user
def addCollect(request):
    u_id = request.session.get('id', '')
    user = User.objects.get(id=u_id)
    # if request.method == 'POST':

    # 记录收藏博客的id
    col_id = request.POST.get('col_id', '')
    article = Article.objects.get(id=col_id)

    print(col_id)
    records = Collect.objects.filter(user=user, article_id=col_id)

    if records:
        records.delete()
        # 减少收藏数
        article.nums_del()
        return HttpResponse('{"col_state": "success", "col_msg": "添加收藏"}', content_type='application/json')
    else:
        # 增加收藏
        article.nums()
        user_col = Collect()
        print(user_col)
        if col_id:
            user_col.article_id = col_id
            user_col.user_id = u_id
            user_col.save()
            print(col_id)
            return HttpResponse('{"col_state": "success", "col_msg": "取消收藏"}', content_type='application/json')


# 我的收藏
@check_user
def my_collect(request):
    u_id = request.session.get('id', '')
    user = User.objects.get(id=u_id)
    all_collect = Collect.objects.filter(user_id=u_id)
    paginator = Paginator(all_collect, 3)  # 每页3条数据
    page = request.GET.get('page', 1)  # 默认跳转到第一页
    all_collect = paginator.page(page)
    if all_collect:
        print(all_collect[0].article)
        return render(request, 'blog/my_collect.html', {'all_collect': all_collect, 'user': user})
    else:
        return HttpResponse('还没有任何收藏哦')


# 我的收藏中  取消收藏
@check_user
def cancelCol(request, blog_id):
    u_id = request.session.get('id', '')
    user = User.objects.get(id=u_id)
    col = Collect.objects.filter(user=user, article_id=blog_id)
    col.delete()
    return redirect('blog:my_collect')
