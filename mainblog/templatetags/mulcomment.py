#!/usr/bin/env python
# Version = 3.5.2
# __auth__ = '无名小妖'
from django.utils.safestring import mark_safe
from django import template

register = template.Library()
TEMP1 = """
        <div>
            <span class="GetNick" style='margin-left:%s'>%s</span>
            <span name="recontent" class="%s">：%s</span>
            <span class="reply">
                <a name="DoReply">回复</a>
            </span>
        """


def generate_comment_html(sub_comment_dic, magin_left_val):
    html = '<div>'
    for k, v_dic in sub_comment_dic.items():
        html += TEMP1 % (magin_left_val,k[3],k[0],k[1])
        if v_dic:
            magin_left_val = int(magin_left_val[:2])
            magin_left_val += 30
            html += generate_comment_html(v_dic, str(magin_left_val)+'px')
        html += "</div>"
    html += "</div>"
    return html


@register.simple_tag
def tree(comment_dict):
    html = '<div class="comment">'
    for k, v in comment_dict.items():
        html += TEMP1 % (0, k[3], k[0],k[1])
        html += generate_comment_html(v, '30px')
        html += "</div>"
    html += '</div>'
    return mark_safe(html)
