#!/usr/bin/env python
#-*-coding:utf-8-*-
from django import  template
from django.utils.html import format_html
from CMDB_Server import models
register=template.Library()
@register.simple_tag
def pageabs(current_page,loop_page):
    offset_page= abs(current_page-loop_page)
    if offset_page<3:
        if current_page==loop_page:
            page_ele='''<li tabindex="0" aria-controls="table_id" class ="paginate_button active"> <a href="?page=%s">%s</a> </li >'''%(loop_page,loop_page)
        else:
            page_ele= '''<li tabindex="0" aria-controls="table_id" class ="paginate_button "> <a href="?page=%s">%s</a> </li >''' %(loop_page, loop_page)
        return format_html(page_ele)
    else:
        return ''
# @register.simple_tag
# def check_has_perm(request,id):
#     request_user_perm = models.UserPermission.objects.filter(user=request.user)
#     user_perm_list=[]
#     for perm_id in request_user_perm:
#         user_perm_list.append(perm_id.cmdbpermission_id)
#     print('list-----%s-----%s'%(user_perm_list,id))
#     if id in user_perm_list:
#         #return True
#         print('---------------------------')
#         return format_html('''<a href="/cmdb/edit?action=add" class="btn  btn-xs btn-blue" style='margin-right:-10px'><i class="fa fa-plus"></i>增加</a>''')
#     else:
#         return ''

