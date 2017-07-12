from django.shortcuts import render, redirect, HttpResponse
from auth.views import check_login
from mainmodels.models import UserInfo, Blog, Tag, Category, Article, Comment, UpDown
import json
from utils.excsql import exc_sql
import datetime
from utils import comment_tree


@check_login
def index(request, site):
    """
    博主个人首页
    :param request:
    :param site: 博主的网站后缀如：http://xxx.com/wupeiqi.html
    :return:
    """
    blog = Blog.objects.filter(site=site).select_related('user').first()
    if not blog:
        return redirect('/')
    tag_list = Tag.objects.filter(blog=blog)
    category_list =Category.objects.filter(blog=blog)
    blog_id = Blog.objects.filter(site=site).values_list('nid')
    query = """select nid, count(nid) as num,strftime("%Y-%m",create_time) as ctime from mainmodels_article
                    where blog_id={}  group by strftime("%Y-%m",create_time)""".format(blog_id[0][0])
    date_list = exc_sql(query)

    article_list = Article.objects.filter(blog=blog).order_by('-nid').all()

    return render(
        request,
        'blog_index.html',
        {
            'blog': blog,
            'tag_list': tag_list,
            'category_list': category_list,
            'date_list': date_list,
            'article_list': article_list
        }
    )


def article_detail(req, site, article_id):
    """
        博文详细页
        :param request:
        :param site:
        :param nid:
        :return:
        """
    blog = Blog.objects.filter(site=site).select_related('user').first()
    blog_id = Blog.objects.filter(site=site).values_list('nid')
    if 'user_info' in req.session.keys():  # 验证是否登录
        flag = True
    else:
        flag = False
    tag_list = Tag.objects.filter(blog=blog)
    category_list = Category.objects.filter(blog=blog)
    query = """select nid, count(nid) as num,strftime("%Y-%m",create_time) as ctime from mainmodels_article
                where blog_id={}  group by strftime("%Y-%m",create_time)""".format(blog_id[0][0])
    date_list = exc_sql(query)
    article = Article.objects.filter(blog=blog, nid=article_id).select_related('category', 'articledetail').first()
    # comment_list = Comment.objects.filter(article=article).select_related('reply')
    # print(comment_list)
    comment_q = """select a.nid, a.content, a.create_time, b.nickname, a.reply_id, c.nickname
                    from mainmodels_comment a, mainmodels_userinfo b
                    left join mainmodels_userinfo c on c.nid=a.reply_user_id
                    where a.article_id = {} and b.nid = a.user_id  """.format(article_id)
    comment_list = exc_sql(comment_q)
    comment_dict = comment_tree.build_tree(comment_list)
    # comment_dict = comment_tree.build_tree(comment_list)
    # print(comment_dict)
    if req.POST:
        # 处理点赞
        if req.POST.get('class'):
            val = req.POST.get('class')
            msg = {'status': False, 'message': None}
            f = {}
            f['article_id'] = val.split(' ')[1]
            f['user_id'] = val.split(' ')[0]
            blog_id = Blog.objects.filter(user_id=val.split(' ')[0]).values('nid')
            cn = UpDown.objects.filter(**f).count()
            if cn:
                UpDown.objects.filter(**f).delete()
                obj = Article.objects.filter(nid=val.split(' ')[1], blog_id=blog_id)
                up_count = obj.values_list('up_count')
                obj.update(up_count=int(up_count[0][0]) - 1)
            else:
                f['up'] = 1
                UpDown.objects.create(**f)
                obj = Article.objects.filter(nid=val.split(' ')[1], blog_id=blog_id)
                up_count = obj.values_list('up_count')
                obj.update(up_count=int(up_count[0][0]) + 1)
            msg['status'] = True
            return HttpResponse(json.dumps(msg))
        # 处理点赞 --end--
        # 处理回复
        elif req.POST.get('textarea'):
            msg = {'status': False, 'message': None}
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            user_id = Blog.objects.filter(site=site).values_list('user_id')
            if req.POST.get('recontent'):
                content = req.POST.get('textarea').split(' ')
                content.pop(0)
                content = ''.join(content)
                reply_comm_id = int(req.POST.get('recontent'))
                reply_user_id = Comment.objects.filter(nid=reply_comm_id).values_list('user_id')
                Comment.objects.create(content=content, create_time=now, article_id=article_id,
                                       user_id=user_id[0][0], reply_id=reply_comm_id,reply_user_id=reply_user_id[0][0])
                msg['status'] = True
                return HttpResponse(json.dumps(msg))
            else:
                content = req.POST.get('textarea')
                Comment.objects.create(content=content,create_time=now,article_id=article_id,user_id=user_id[0][0])
                msg['status'] = True
                return HttpResponse(json.dumps(msg))
            # 处理回复 --end--
    return render(
        req,
        'blog_detail.html',
        {
            'blog': blog,
            'article': article,
            'comment_dict': comment_dict,
            'tag_list': tag_list,
            'category_list': category_list,
            'date_list': date_list,
            'flag': flag,
        }
    )


@check_login
def article_filter(request, site, condition, val):
    """
    分类显示
    :param request:
    :param site:
    :param condition:
    :param val:
    :return:
    """
    blog = Blog.objects.filter(site=site).select_related('user').first()
    blog_id = Blog.objects.filter(site=site).values_list('nid')
    if not blog:
        return redirect('/')
    tag_list = Tag.objects.filter(blog=blog)
    category_list = Category.objects.filter(blog=blog)
    query = """select nid, count(nid) as num,strftime("%Y-%m",create_time) as ctime from mainmodels_article
                    where blog_id={}  group by strftime("%Y-%m",create_time)""".format(blog_id[0][0])
    date_list = exc_sql(query)

    template_name = "blog_summary_list.html"
    if condition == 'tag':
        template_name = "blog_title_list.html"
        article_list = Article.objects.filter(tag_id=val, blog=blog).all()
    elif condition == 'category':
        article_list = Article.objects.filter(category_id=val, blog=blog).all()
    elif condition == 'date':
        article_list = Article.objects.filter(blog=blog).extra(
            where=['strftime("%%Y-%%m",create_time)=%s'], params=[val, ]).all()
    else:
        article_list = []

    return render(
        request,
        template_name,
        {
            'blog': blog,
            'tag_list': tag_list,
            'category_list': category_list,
            'date_list': date_list,
            'article_list': article_list
        }
    )