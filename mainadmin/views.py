from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse
from auth.views import check_login
import os
import json
from mainmodels.models import UserInfo, Blog, Tag, Category, Article, ArticleDetail, Comment
from django.db import transaction
from utils.xss import XSSFilter
from mainadmin.forms import ArticleForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@check_login
def index(req):
    site = req.session.get('user_info')['blog__site']
    return render(req, 'admin_index.html', {'blog_site': site})


@check_login
def edit_article(req, **kwargs):
    if req.POST:  # 删除数据
        msg = {'status': False, 'message': None}
        Article.objects.filter(nid=req.POST.get('nid')).delete()
        msg['status'] = True
        return HttpResponse(json.dumps(msg))
    category = Category.objects.all().values('nid', 'title')
    tag = Tag.objects.all().values('nid', 'title')
    site = req.session.get('user_info')['blog__site']
    choice_dict = kwargs  # 组合搜索使用
    condition = {}  # 过滤文章使用
    condition['blog_id'] = req.session.get('user_info')['blog__nid']
    for k, v in kwargs.items():
        kwargs[k] = int(v)
        if v == '0':
            pass
        else:
            condition[k] = v
    article_cn = Article.objects.filter(**condition).count()

    contact_list = Article.objects.filter(**condition)
    paginator = Paginator(contact_list, 5)  # Show 10 contacts per page
    page = req.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)

    return render(req, 'admin_edit_article.html',
                  {'category': category,
                   'tag': tag,
                   'blog_site': site,
                   'choice_dict': choice_dict,
                   'num': article_cn,
                   'contacts': contacts})


@check_login
def add_article(request):
    """
    添加文章
    :param request:
    :return:
    """
    if request.method == 'GET':
        form = ArticleForm(request=request)
        return render(request, 'admin_add_article.html', {'form': form})
    elif request.method == 'POST':
        form = ArticleForm(request=request, data=request.POST)
        if form.is_valid():

            with transaction.atomic():
                content = form.cleaned_data.pop('content')
                content = XSSFilter().process(content)
                form.cleaned_data['blog_id'] = request.session['user_info']['blog__nid']
                obj = Article.objects.create(**form.cleaned_data)
                ArticleDetail.objects.create(content=content, article=obj)

            return redirect('/mainadmin/edit_article_0_0.html')
        else:
            return render(request, 'admin_add_article.html', {'form': form})
    else:
        return redirect('/')


@check_login
def update_article(request, nid):
    """
    编辑文章
    :param request:
    :return:
    """
    blog_id = request.session['user_info']['blog__nid']
    site = request.session.get('user_info')['blog__site']
    if request.method == 'GET':
        obj = Article.objects.filter(nid=nid, blog_id=blog_id).first()
        if not obj:
            return render(request, 'admin_no_article.html')
        tag_id = obj.tag_id
        init_dict = {
            'nid': obj.nid,
            'title': obj.title,
            'summary': obj.summary,
            'category_id': obj.category_id,
            'article_type_id': obj.article_type_id,
            'content': obj.articledetail.content,
            'tag_id': tag_id
        }
        form = ArticleForm(request=request, data=init_dict)
        return render(request, 'admin_update_article.html', {'form': form, 'nid': nid, 'blog_site': site})
    elif request.method == 'POST':
        form = ArticleForm(request=request, data=request.POST)
        if form.is_valid():
            obj = Article.objects.filter(nid=nid, blog_id=blog_id).first()
            if not obj:
                return render(request, 'admin_no_article.html')
            with transaction.atomic():
                content = form.cleaned_data.pop('content')
                content = XSSFilter().process(content)
                Article.objects.filter(nid=obj.nid).update(**form.cleaned_data)
                ArticleDetail.objects.filter(article=obj).update(content=content)

            return redirect('/mainadmin/edit_article_0_0.html')
        else:
            return render(request, 'admin_update_article.html', {'form': form, 'nid': nid, 'blog_site': site})


@check_login
def edit_category(req):
    msg = {'status': False, 'message': None}
    blog_id = req.session.get('user_info')['blog__nid']
    ret = Category.objects.filter(blog_id=blog_id)
    site = req.session.get('user_info')['blog__site']
    if req.POST:
        title = req.POST.get('title')
        if title and blog_id:  # 添加数据
            Category.objects.create(title=title, blog_id=blog_id)
            msg['status'] = True
            return HttpResponse(json.dumps(msg))
        elif req.POST.get('nid'):  # 删除数据
            Category.objects.filter(nid=req.POST.get('nid')).delete()
            msg['status'] = True
            return HttpResponse(json.dumps(msg))
    return render(req, 'admin_edit_category.html', {'ret': ret, 'blog_site': site, })


@check_login
def update_category(req, nid):
    site = req.session.get('user_info')['blog__site']
    msg = {'status': False, 'message': None}
    ret = Category.objects.filter(nid=nid).values_list('nid', 'title')
    if req.POST:
        Category.objects.filter(nid=req.POST.get('nid')).update(title=req.POST.get('title'))
        msg['status'] = True
        return HttpResponse(json.dumps(msg))
    return render(req, 'admin_update_category.html', {'item': ret, 'blog_site': site})


@check_login
def edit_tag(req):
    msg = {'status': False, 'message': None}
    blog_id = req.session.get('user_info')['blog__nid']
    ret = Tag.objects.filter(blog_id=blog_id)
    site = req.session.get('user_info')['blog__site']
    if req.POST:
        title = req.POST.get('title')
        if title and blog_id:  # 添加数据
            Tag.objects.create(title=title, blog_id=blog_id)
            msg['status'] = True
            return HttpResponse(json.dumps(msg))
        elif req.POST.get('nid'):  # 删除数据
            Tag.objects.filter(nid=req.POST.get('nid')).delete()
            msg['status'] = True
            return HttpResponse(json.dumps(msg))
    return render(req, 'admin_edit_tag.html', {'ret': ret, 'blog_site': site})


@check_login
def update_tag(req, nid):
    site = req.session.get('user_info')['blog__site']
    msg = {'status': False, 'message': None}
    ret = Tag.objects.filter(nid=nid).values_list('nid', 'title')
    if req.POST:
        Tag.objects.filter(nid=req.POST.get('nid')).update(title=req.POST.get('title'))
        msg['status'] = True
        return HttpResponse(json.dumps(msg))
    return render(req, 'admin_update_tag.html', {'item': ret, 'blog_site': site})


@check_login
def edit_base_info(req):
    site = req.session.get('user_info')['blog__site']
    msg = {'status': False, 'message': None}
    if req.POST:
        nickname = req.POST.get('nickname')
        site = req.POST.get('site')
        gender = req.POST.get('gender')
        user_id = req.POST.get('user_id')
        if nickname:
            UserInfo.objects.filter(nid=user_id).update(nickname=nickname)
        if gender:
            UserInfo.objects.filter(nid=user_id).update(gender=gender)
        if site:
            Blog.objects.create(user_id=user_id, site=site, title=site, theme='default')
        # 如果图片路径下有和登录用户名相同的图片，将头像标识置为1
        file_path = os.path.join('static/imgs/avatar', req.session.get('user_info')['username'] + '.png')
        if os.path.isfile(file_path):
            UserInfo.objects.filter(nid=user_id).update(avatar=1)
        # 以下重置session中的user_info，以便刷新页面数据
        user_info = UserInfo.objects.filter(nid=user_id). \
            values('nid', 'nickname', 'username', 'email', 'gender',
                   'avatar', 'blog__nid', 'blog__site').first()
        if user_info:
            req.session['user_info'] = user_info
        msg['status'] = True

        return HttpResponse(json.dumps(msg))
    return render(req, 'admin_base_info.html', {'blog_site': site})


@check_login
def upload_avatar(request):
    ret = {'status': False, 'data': None, 'message': None}
    if request.method == 'POST':
        file_obj = request.FILES.get('avatar_img')
        if file_obj:
            file_name = request.session.get('user_info')['username'] + '.png'
            file_path = os.path.join('static/imgs/avatar', file_name)
            f = open(file_path, 'wb')
            for chunk in file_obj.chunks():
                f.write(chunk)
            f.close()
            ret['status'] = True
            ret['data'] = file_path
    return HttpResponse(json.dumps(ret))



