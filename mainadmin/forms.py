from django import forms as django_forms
from django.forms import fields as django_fields
from django.forms import widgets as django_widgets
from mainmodels import models


class ArticleForm(django_forms.Form):
    title = django_fields.CharField(error_messages={'required': ' >>错误提示：标题不能为空'},
        widget=django_widgets.TextInput(attrs={'class': 'form-control', 'placeholder': '文章标题'},)
    )
    summary = django_fields.CharField(error_messages={'required': ' >>错误提示：简介不能为空'},
        widget=django_widgets.Textarea(attrs={'class': 'form-control', 'placeholder': '文章简介', 'rows': '3'})
    )
    content = django_fields.CharField(error_messages={'required': ' >>错误提示：内容不能为空'},
        widget=django_widgets.Textarea(attrs={'class': 'kind-content'})
    )
    article_type_id = django_fields.IntegerField(error_messages={'required': ' >>错误提示：请选择文章类型！'},
        widget=django_widgets.RadioSelect(choices=models.Article.type_choices)
    )
    category_id = django_fields.ChoiceField(error_messages={'required': ' >>错误提示：请选择文章分类'},
        widget=django_widgets.RadioSelect
    )
    tag_id = django_fields.ChoiceField(error_messages={'required': ' >>错误提示：请选择文章标签'},
        widget=django_widgets.RadioSelect
    )

    def __init__(self, request, *args, **kwargs):
        super(ArticleForm, self).__init__(*args, **kwargs)
        blog_id = request.session['user_info']['blog__nid']
        self.fields['category_id'].choices = models.Category.objects.filter(blog_id=blog_id).values_list('nid',
                                                                                                         'title')
        self.fields['tag_id'].choices = models.Tag.objects.filter(blog_id=blog_id).values_list('nid', 'title')

