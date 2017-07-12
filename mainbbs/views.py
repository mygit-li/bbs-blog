from django.shortcuts import render, reverse, HttpResponse
from mainmodels.models import Article, UpDown, Blog
from utils.pagination import Pagination
from utils.excsql import exc_sql
import json


def index(request, *args, **kwargs):
    """
    博客首页，展示全部博文
    :param request:
    :return:
    """

    article_type_list = Article.type_choices

    if kwargs:
        article_type_id = int(kwargs['article_type_id'])
        sql = """select a.title,a.summary,a.up_count,a.comment_count,c.nickname,c.username,a.read_count,a.nid,
                 strftime("%Y-%m-%d %H:%M:%S",a.create_time) as ctime, b.user_id, b.site from mainmodels_article a,
                 mainmodels_blog b, mainmodels_userinfo c where a.blog_id=b.nid and b.user_id=c.nid  and
                 a.article_type_id={} order by a.nid desc""".format(article_type_id)
        base_url = reverse('index', kwargs=kwargs)
        data_count = Article.objects.filter(article_type_id=article_type_id).count()
    else:
        sql = """select a.title,a.summary,a.up_count,a.comment_count,c.nickname,c.username,a.read_count,a.nid,
                 strftime("%Y-%m-%d %H:%M:%S",a.create_time) as ctime, b.user_id, b.site from mainmodels_article a,
                 mainmodels_blog b, mainmodels_userinfo c where a.blog_id=b.nid and b.user_id=c.nid
                 order by a.nid desc"""
        article_type_id = None
        base_url = '/mainbbs/bbs_index.html'
        data_count = Article.objects.all().count()

    page_obj = Pagination(request.GET.get('p'), data_count)
    sql_ret = exc_sql(sql)
    article_list = sql_ret[page_obj.start:page_obj.end]
    page_str = page_obj.page_str(base_url)

    pinglun = """select a.nid,a.title,c.username from mainmodels_article a, mainmodels_blog b, mainmodels_userinfo c
                 where a.blog_id = b.nid   and b.user_id = c.nid order by a.comment_count desc limit 5"""
    ping_lun = exc_sql(pinglun)

    tuijian = """select a.nid,a.title,c.username  from mainmodels_article a, mainmodels_blog b, mainmodels_userinfo c
                  where a.blog_id = b.nid   and b.user_id = c.nid order by a.read_count desc limit 5"""
    tui_jian = exc_sql(tuijian)

    # 处理点赞
    if request.POST:
        msg = {'status': False, 'message': None}
        val = request.POST.get('class')
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
        print(request.path_info)
        return HttpResponse(json.dumps(msg))
    # 处理点赞 --end--
    return render(
        request,
        'bbs_index.html',
        {
            'article_list': article_list,
            'article_type_id': article_type_id,
            'article_type_list': article_type_list,
            'page_str': page_str,
            'ping_lun': ping_lun,
            'tui_jian': tui_jian,
        }
    )
