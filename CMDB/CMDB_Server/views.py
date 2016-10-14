#!/usr/bin/env python
#-*-coding:utf-8-*-
from django.shortcuts import render,HttpResponseRedirect,HttpResponse,Http404,render_to_response
from django.contrib.auth import logout,login,authenticate
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import PBKDF2PasswordHasher,make_password
from django.views.decorators.csrf import csrf_exempt
from CMDB_Server import models
from datahandler import DataHandler
from  permission import check_permission,check_has_perm
import time,json,logging
# Create your views here.
logger=logging.getLogger('cmdb.views')
def get_client_ip(request):
    try:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    except Exception as e:
        logger.error(e.message)
def main(request):
    return render(request,'login.html')
def acclogin(request):
    login_err=""
    try:
        if request.method=="POST":
            user=authenticate(username=request.POST.get('username'),password=request.POST.get('password'))
            if user:
                if user.is_active:
                    login(request,user)
                    login_err='%s login success'%request.user.username
                    logger.info("IP:%s %s"%(get_client_ip(request),login_err))
                    return HttpResponseRedirect('/cmdb/')
                else:
                    login_err = "%s user is locked..." % request.user.username
            else:
                login_err = " Username or Password is wrong"
            logger.warning("IP:%s %s %s"%(get_client_ip(request),request.POST.get('username'),login_err))
    except Exception as e:
        logger.error(e.message)
    return render(request, 'login.html', {'login_err':login_err})
def acclogout(request):
    logger.info("IP:%s %s logout" % (get_client_ip(request),request.user.username))
    logout(request)
    return HttpResponseRedirect('/accounts/login/')
@login_required
def index(request):
    asset_count=models.Asset.objects.all().count()
    return render(request,'cmdb/index.html',{'assetcount':asset_count})
@csrf_exempt
def recvdata(request):
    try:
        if request.method=='POST':
            asset_dic=json.loads(request.POST.get('data'))
            handler=DataHandler(asset_dic)
            handler.datahandler()
            ret_data=json.dumps({'asset_id':handler.assetid})
        return HttpResponse(ret_data)
    except Exception as e:
        logger.error(e.message)
@login_required
def asset(request):
    asset_obj=models.Asset.objects.all()
    paginator = Paginator(asset_obj, 20)  # Show 25 contacts per page
    page = request.GET.get('page')
    try:
        assetpage = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        assetpage = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        assetpage = paginator.page(paginator.num_pages)
    return render(request,'cmdb/asset.html',{'assetobj':assetpage,'add_perm':check_has_perm(request,1),'edit_perm':check_has_perm(request,2),'del_perm':check_has_perm(request,3)})
    #return render(request,'cmdb/asset.html',{'assetobj':assetpage})
@login_required
def server(request):
    server_obj=models.Asset.objects.filter(asset_type='server')
    return render(request,'cmdb/server.html',{'serverobj':server_obj})
@login_required
def detail(request,assetid):
    asset_obj=models.Asset.objects.get(id=assetid)
    return render(request, 'cmdb/detail.html', {'assetobj':asset_obj})
@check_permission
@login_required
def edit(request):
    if request.method=='GET':
        idc_obj = models.IDC()
        user_obj = models.User.objects.all()
        if request.GET['action']=='add':
            asset_obj=models.Asset()
            retrender=render(request,'cmdb/edit.html',{'assetobj':asset_obj,'idcobj':idc_obj,'userobj':user_obj})
        elif request.GET['action']=='edit':
            if request.GET['id']:
                asset_obj=models.Asset.objects.get(id=request.GET['id'])
                retrender = render(request, 'cmdb/edit.html', {'assetobj': asset_obj, 'idcobj': idc_obj, 'userobj': user_obj})
        elif request.GET['action'] == 'del':
            if request.GET['id']:
                asset_obj = models.Asset.objects.get(id=request.GET['id']).delete()
                retrender = HttpResponseRedirect('/cmdb/asset/')
                logger.warning("%s %s manual del asset data,assetid:%s"%(get_client_ip(request),request.user.username,request.GET['id']))
        # elif request.GET['action'] == 'line':
        #     if request.GET['id']:
        #         asset_obj = models.Asset.objects.get(id=request.GET['id'])
        #         if asset_obj.asset_status==1:
        #             models.Asset.objects.filter(id=request.GET['id']).update(asset_status=2)
        #         else:
        #             models.Asset.objects.filter(id=request.GET['id']).update(asset_status=1)
        #         ret = HttpResponseRedirect('/cmdb/asset/')
        else:
            logger.warning('request asset info failure,reqeust get action error')
        return retrender
    else:
        try:
            data = request.POST
            if data.get('id')=="None":
                new_asset_obj = models.Asset(assetno=data.get('assetno'), asset_type=data.get('asset_type'),sn=data.get('sn'), servermodel=data.get('servermodel'),business_ip=data.get('management_ip'), release_date=data.get('release_date'),business_unit=data.get('business_unit'), tags=data.get('tags'),admin_id=data.get('admin'), idc_id=data.get('idc'),idc_cabinet=data.get('idc_cabinet'), create_type=data.get('create_type'),asset_status=data.get('asset_status'))
                new_asset_obj.save()
                logger.info("%s %s manual add new asset data,assetid:%s"%(get_client_ip(request),request.user.username,new_asset_obj.id))
            else:
                models.Asset.objects.filter(id=data.get('id')).update(assetno=data.get('assetno'), asset_type=data.get('asset_type'),sn=data.get('sn'), servermodel=data.get('servermodel'),business_ip=data.get('management_ip'), release_date=data.get('release_date'),business_unit=data.get('business_unit'), tags=data.get('tags'),admin_id=data.get('admin'), idc_id=data.get('idc'),idc_cabinet=data.get('idc_cabinet'), create_type=data.get('create_type'),asset_status=data.get('asset_status'))
                logger.info('%s %s manual modify asset data,assetid:%s'%(get_client_ip(request),request.user.username,data.get('id')))
            return HttpResponseRedirect('/cmdb/asset/')
        except Exception as e:
            logger.error(e.message)
@login_required
def idc(request):
    idc_object=models.IDC.objects.all()
    return render(request, 'cmdb/idc.html', {'idcobj':idc_object})
def graph(request):
    idc_object=models.IDC.objects.all()
    return render(request, 'cmdb/graph.html', {'idcobj':idc_object})
@login_required
def os(request):
    asset_object=models.Asset.objects.filter(asset_status=2,asset_type='server')
    return render(request, 'cmdb/os.html', {'assetobj':asset_object})
@check_permission
@login_required
def createuser(request):
    user_list = models.User.objects.filter(is_active=1)
    perm_list=models.CmdbPermission.objects.all()[:5]
    useredit_obj=models.User()
    if request.method=="GET":
        try:
            if request.GET['action']=='edit':
                if request.GET['id']:
                    useredit_obj=models.User.objects.get(id=request.GET['id'])
                    #return render(request, 'cmdb/user.html', {'userobj': user_list, 'usereditobj': useredit_obj,'permlist':perm_list})
            elif request.GET['action']=='del':
                if request.GET['id']:
                    models.User.objects.filter(id=request.GET['id']).delete()
        except Exception as e:
            pass

    else:
        data=request.POST
        if data.get('id') == 'None':
            user_obj=models.User(username=data.get('username'), password=make_password(data.get('password')),email=data.get('email'), is_superuser=int(data.get('superuser')))
            user_obj.save()
            logger.info('%s %s create new user,userid:%s' % (get_client_ip(request), request.user.username, user_obj.id))
        elif data.get('id'):
            print('-------', data)
            models.User.objects.filter(id=data.get('id')).update(username=data.get('username'),email=data.get('email'), is_superuser=int(data.get('superuser')))
            logger.info('%s %s modify user info,userid:%s' % (get_client_ip(request), request.user.username, data.get('id')))
        if data.get('changeusername'):
            models.User.objects.filter(id=request.POST.get('changeusername')).update(password=make_password(request.POST.get('password')))
            logger.info( '%s %s change password,userid:%s' % (get_client_ip(request), request.user.username,request.POST.get('changeusername')))
        if data.get('user_perm1'):
            for perm in request.POST.getlist('user_perm1'):
                perm_obj=models.UserPermission.objects.create(user_id=data.get('username'),cmdbpermission_id=perm)
                perm_obj.save()
                try:
                    perm_other=models.CmdbPermission.objects.exclude(id=perm).get(name=perm_obj.cmdbpermission.name)
                    if perm_other:
                        models.UserPermission.objects.create(user_id=data.get('username'),cmdbpermission_id=perm_other.id)
                    logger.info('%s %s add %s premission,userid:%s' % (get_client_ip(request), request.user.username,perm_obj.cmdbpermission.name, data.get('username')))
                except Exception as e:
                    logger.error(e.message)
    return render(request,'cmdb/user.html',{'userobj':user_list, 'usereditobj': useredit_obj,'permlist':perm_list})
def cmdbpermission(request):
    user_obj=models.User.objects.get(id=request.POST.get('id'))
    user_perm_obj=models.UserPermission.objects.filter(user_id=request.POST.get('id'))
    user_perm_list=[]
    if not user_obj.is_superuser:
        for user_perm in user_perm_obj:
            user_perm_list.append(user_perm.cmdbpermission_id)
    return HttpResponse(json.dumps(user_perm_list))
# def page_not_found(request):
#     return render_to_response('404.html')

def log(request):
    return render(request,'cmdb/log.html')


