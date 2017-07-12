#!/usr/bin/env python
# Version = 3.5.2
# __auth__ = '无名小妖'
from django import forms
from mainmodels.models import *
from django.core.exceptions import ValidationError


class RegisterForm(forms.Form):
    """添加用户验证"""
    # django给标签加sytle，关键参数widget ，forms.TextInput 表示生成type="text"的input标签，改成Textarea则生成<textarea>标签
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}),
                               error_messages={'required': '不能为空',})
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                               min_length=6,
                               max_length=10,
                               error_messages={'required': '不能为空', 'min_length': '至少6位',
                                               'max_length': '至多10位'})
    confirm_password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                                       min_length=6,
                                       max_length=10,
                                       error_messages={'required': '不能为空', 'min_length': '至少6位',
                                                       'max_length': '至多10位'})
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}),
                             error_messages={'required': '邮箱不能为空', 'invalid': '邮箱格式错误'},)


class LoginForm(forms.Form):
    """登录表单验证"""
    # 下面使用的变量名必须和html中input标签的name值相同
    # forms 的字段类型包括：IntegerField,CharField,URLField,EmailField,DateField等，但是没有手机号
    # required=True表示对输入做验证
    # error_messages 自定制提示信息
    # django给标签加sytle,关键参数widget,forms.TextInput表示生成type="text"的input标签，改成PasswordInput则type="password"
    username = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}),
                               error_messages={'required': '用户名不能为空'})
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                               min_length=6,
                               max_length=10,
                               error_messages={'required': '密码不能为空', 'min_length': '至少6位',
                                               'max_length': '至多10位'})
