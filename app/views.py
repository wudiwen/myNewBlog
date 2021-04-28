import hashlib

from PIL import Image
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.cache import cache_page

from app.models import User
from app.forms import CommentForm, ArticleForm, ProfileForm


# Create your views here.

@cache_page(60)
def index(request):
    return render(request, 'account/index.html')


def login(request):
    if request.method == 'POST':
        user_name = request.POST.get('username')
        pass_word = request.POST.get('password')
        # 将输入密码换成注册时生成的摘要，此时数据库中是加密后的密码
        md5 = hashlib.md5()
        md5.update(pass_word.encode('utf-8'))
        pass_word = md5.hexdigest()
        # 查看数据库里是否有该用户
        user = User.objects.filter(username=user_name)
        if user:
            # 读取该用户信息
            user = User.objects.get(username=user_name)
            if pass_word == user.password:
                request.session['IS_LOGIN'] = True
                request.session['nickname'] = user.nickname
                request.session['username'] = user_name
                request.session['id'] = user.pk
                # print(request.session.get('id', ''))
                # return render(request, 'login_success.html', {'user': user})
                return redirect('account:login_success')
            else:
                return render(request, 'account/login.html', {'error': '密码错误'})
        else:
            return render(request, 'account/login.html', {'error': '用户名不存在'})
    elif request.session.get('IS_LOGIN', ''):
        print(1)
        # user = request.session.get('id', '')
        # user = User.objects.get(id=user)
        # return render(request, 'login_success.html', {'user': user})
        return redirect('account:login_success')
        # return redirect('blog:login_success', {'user': user})
    else:
        return render(request, 'account/login.html')


# 验证是否登录
def check_user(func):
    def inner(*args, **kwargs):
        is_login = args[0].session.get('IS_LOGIN', '')
        if is_login != True:
            # 把当前url保存到session中
            args[0].session['path'] = args[0].path
            return redirect(reverse('account:login'))
        return func(*args, **kwargs)

    return inner


@check_user
def login_success(request):
    user = request.session.get('id', '')
    print('45465465465464', user)
    user = User.objects.get(id=user)
    return render(request, 'account/login_success.html', {'user': user})


def logout(requset):
    # 清除用户登录状态
    requset.session.flush()
    return render(requset, 'account/login.html')


def register(request):
    if request.method == 'POST':
        user_name = request.POST.get('username', '')
        pass_word1 = request.POST.get('password_1', '')
        pass_word2 = request.POST.get('password_2', '')
        nick_name = request.POST.get('nickname', '')
        email = request.POST.get('email', '')
        avatar = request.FILES.get('icon')
        if User.objects.filter(username=user_name):
            return render(request, 'account/register.html', {'error': '用户已存在'})
        if User.objects.filter(email=email):
            return render(request, 'account/register.html', {'error': '该邮箱已绑定用户'})
        # 表单数据写入数据库
        if pass_word1 != pass_word2:
            return render(request, 'account/register.html', {'error': '密码不一致'})

        # 密码加密
        md5 = hashlib.md5()
        md5.update(pass_word1.encode('utf-8'))
        pass_word1 = md5.hexdigest()
        user = User()

        if avatar:
            user.icon = 'media/' + user_name + '.png'
            img_circle = setIcon(avatar)
            img_circle.save('app/static/media/' + user_name + '.png')

        user.username = user_name
        user.password = pass_word1
        user.email = email
        user.nickname = nick_name
        user.save()
        # 返回注册成功的页面
        return redirect('account:login')
    else:
        return render(request, 'account/register.html')


# 忘记密码
def forget_password(request):
    if request.method == 'POST':
        user_name = request.POST.get('username', '')
        email = request.POST.get('email', '')
        user = User.objects.filter(username=user_name)
        if user:
            user = User.objects.get(username=user_name)
            if user.email == email:
                request.session['username'] = user_name
                return render(request, 'account/reset.html')
            else:
                return render(request, 'account/forget.html', {'error': '用户名和邮箱不一致'})
        else:
            return render(request, 'account/forget.html', {'error': '请输入正确的用户名'})
    else:
        return render(request, 'account/forget.html')


# 重置密码
def reset(request):
    if request.method == 'POST':
        pass_word1 = request.POST.get('password1', '')
        pass_word2 = request.POST.get('password2', '')
        user_name = request.session['username']
        user = User.objects.get(username=user_name)
        if pass_word1 == pass_word2:
            md5 = hashlib.md5()
            md5.update(pass_word1.encode('utf-8'))
            pass_word1 = md5.hexdigest()
            user.password = pass_word1
            user.save()
            return render(request, 'account/login.html')
        else:
            return render(request, 'account/reset.html', {'error': '两次的密码不一致'})
    else:
        return render(request, 'account/reset.html')


# 更改用户信息
def profile_edit(request, u_id):
    user = User.objects.get(id=u_id)
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES)

        if profile_form.is_valid():
            profile_cd = profile_form.cleaned_data
            user.nickname = profile_cd['nickname']
            # user.icon = profile_cd['icon']
            user.save()
            return redirect('account:login_success')
        else:
            print(profile_form.errors)
            return HttpResponse('表单有问题')
    else:
        profile_form = ProfileForm()
        content = {
            'profile_form': profile_form,
            'user': user,
        }
        return render(request, 'account/profile_edit.html', content)


# 上传头像
def upload(request, u_id):
    user = User.objects.get(id=u_id)
    if request.method == 'POST':
        icon = request.FILES.get('icon', '')
        if icon:
            user.icon = 'media/' + user.username + '.png'
            # 处理图片
            img_circle = setIcon(icon)
            img_circle.save('app/static/media/' + user.username + '.png')
        user.save()
        print('=======================')
        return redirect('account:login_success')
    else:
        return render(request, 'account/upload.html', {'user': user})


# 将图片修改为圆形
def setIcon(icon):
    img = Image.open(icon)
    size = img.size
    print(size)
    # 因为是要圆形，所以需要正方形的图片
    r2 = min(size[0], size[1])
    if size[0] != size[1]:
        img = img.resize((r2, r2), Image.ANTIALIAS)
    # 最后生成圆的半径
    r3 = int(r2 / 2)
    img_circle = Image.new('RGBA', (r3 * 2, r3 * 2), (255, 255, 255, 0))
    pima = img.load()  # 像素的访问对象
    pimb = img_circle.load()
    r = float(r2 / 2)  # 圆心横坐标
    for i in range(r2):
        for j in range(r2):
            lx = abs(i - r)  # 到圆心距离的横坐标
            ly = abs(j - r)  # 到圆心距离的纵坐标
            l = (pow(lx, 2) + pow(ly, 2)) ** 0.5  # 三角函数 半径

            if l < r3:
                pimb[i - (r - r3), j - (r - r3)] = pima[i, j]
    return img_circle
