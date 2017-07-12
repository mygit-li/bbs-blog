#!/usr/bin/env python
# Version = 3.5.2
# __auth__ = '无名小妖'
import collections


def tree_search(d_dic, comment_obj):
    for k, v_dic in d_dic.items():
        if k[0] == comment_obj[4]:
            d_dic[k][comment_obj] = collections.OrderedDict()
            return
        else:
            tree_search(d_dic[k], comment_obj)


def build_tree(l_list):
    # 创建有序字典
    comment_dict = collections.OrderedDict()
    for comment_obj in l_list:
        if comment_obj[4] is None:
            # 如果是根评论，添加到comment_dict[评论对象] = {}
            comment_dict[comment_obj] = collections.OrderedDict()
        else:
            # 如果是回复的评论，则需要在comment_dict中找到回复的谁
            tree_search(comment_dict,comment_obj)
    return comment_dict
