from django.shortcuts import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
import json
from io import BytesIO
from mybbs.check_code import create_validate_code
from mybbs.forms import *
from mainmodels.models import UserInfo
import datetime
import hashlib


def check_code(req):
    """
    生成验证码函数
    :param req: 表单发送的请求数据
    :return: 返回内存中的验证码信息
    """
    stream = BytesIO()
    img, code = create_validate_code()
    img.save(stream, "png")
    req.session["CheckCode"] = code
    return HttpResponse(stream.getvalue())


def encrypt(string):
    """
    字符串加密函数
    :param string: 待加密的字符串
    :return:  返回加密过的字符串
    """
    ha = hashlib.md5(b'hys')
    ha.update(string.encode('utf-8'))
    result = ha.hexdigest()
    return result


def register(req):
    """
    注册函数
    :param req:
    :return:  返回渲染页面
    """
    msg = {'status': False, 'message': None}
    if req.POST:
        obj = RegisterForm(req.POST)
        if obj.is_valid():
            if req.POST.get('checkcode').upper() == req.session['CheckCode'].upper():
                user = UserInfo.objects.filter(username__exact=obj.cleaned_data['username'])
                email = UserInfo.objects.filter(email__exact=obj.cleaned_data['email'])
                if user:
                    msg['message'] = {"username": [{"message": "用户名已被注册", "code": "invalid"}]}
                    return HttpResponse(json.dumps(msg))
                elif email:
                    msg['message'] = {"email": [{"message": "邮箱已被注册", "code": "invalid"}]}
                    return HttpResponse(json.dumps(msg))
                elif obj.cleaned_data['password'] != obj.cleaned_data['confirm_password']:
                    msg['message'] = {"confirm_password": [{"message": "两次密码不一致", "code": "invalid"}]}
                    return HttpResponse(json.dumps(msg))
                else:
                    obj.cleaned_data.pop('confirm_password')
                    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    obj.cleaned_data['create_time'] = now
                    obj.cleaned_data['password'] = encrypt(obj.cleaned_data['password'])
                    UserInfo.objects.create(**obj.cleaned_data)  # cleaned_data是字典
                    user_info = UserInfo.objects.filter(username=obj.cleaned_data['username'],
                        password=obj.cleaned_data['password']).values('nid', 'nickname', 'username',
                        'email', 'gender', 'avatar', 'blog__nid', 'blog__site').first()
                    if user_info:
                        req.session['user_info'] = user_info
                    msg['status'] = True
                    return HttpResponse(json.dumps(msg))
            else:
                msg['message'] = {"checkcode": [{"message": "验证码错误", "code": "invalid"}]}
                return HttpResponse(json.dumps(msg))
        else:
            print(obj.errors.as_json())
            error_str = obj.errors.as_json()
            msg['message'] = json.loads(error_str)
            return HttpResponse(json.dumps(msg))
    return render(req, 'register.html')


def login(req):
    # 记住用户名密码
    info = {}
    if 'username' in req.COOKIES.keys():
        info['username'] = req.COOKIES['username']
        info['password'] = req.COOKIES['password']
    # 记住用户名密码 --end
    msg = {'status': False, 'message': None}
    if req.POST:
        obj = LoginForm(req.POST)
        if obj.is_valid():
            if req.POST.get('checkcode').upper() == req.session['CheckCode'].upper():
                username = req.POST.get('username')
                password = encrypt(req.POST.get('password'))
                user_info = UserInfo.objects.filter(username=username, password=password). \
                    values('nid', 'nickname', 'username', 'email', 'gender',
                           'avatar', 'blog__nid', 'blog__site').first()
                if user_info:
                    req.session['user_info'] = user_info
                    msg['status'] = True
                    # 记住用户名密码
                    if req.POST.get('checked') == '1':
                        response = HttpResponse(json.dumps(msg))
                        response.set_cookie('username', username)
                        response.set_cookie('password', req.POST.get('password'))
                    else:
                        response = HttpResponse(json.dumps(msg))
                        if 'username' in req.COOKIES.keys():
                            response.set_cookie('username', '')
                            response.set_cookie('password', '')
                    return response
                    # 记住用户名密码 --end
                else:
                    msg['message'] = {"password": [{"message": "用户名或密码错误", "code": "invalid"}]}
                    return HttpResponse(json.dumps(msg))
            else:
                msg['message'] = {"checkcode": [{"message": "验证码错误", "code": "invalid"}]}
                return HttpResponse(json.dumps(msg))
        else:
            msg['message'] = json.loads(obj.errors.as_json())
            return HttpResponse(json.dumps(msg))

    return render(req, 'login.html', {'info': info})


def logout(req):
    req.session.clear()
    return redirect('/login/')
