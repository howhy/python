#!/usr/bin/env python
#-*-coding:utf-8-*-
from django.db import models
from django.contrib.auth.models import  User
# Create your models here.
class CmdbPermission(models.Model):
    name=models.CharField(max_length=32)
    url=models.CharField(max_length=32)
    request_method=models.CharField(max_length=32)
    request_args=models.CharField(max_length=64,null=True)
    request_args_value=models.CharField(max_length=32,null=True)
class UserPermission(models.Model):
     cmdbpermission=models.ForeignKey(CmdbPermission)
     user=models.ForeignKey(User)
class IDC(models.Model):
    idc_choices = ((1, u'广州奥飞IDC'),
                   (2, u'香港IDC'),
                   (3, u'深圳南山IDC'),
                   (4, u'深圳岗厦IDC'))
    name=models.SmallIntegerField(choices=idc_choices,verbose_name=u'IDC名称',default='GZ',null=True)
    location=models.CharField(u'IDC位置',max_length=128)
    contact_name=models.CharField(u'IDC联系人',max_length=32)
    contact_tel=models.CharField(u'联系人电话',max_length=32)
    create_date = models.DateTimeField(u'创建日期', blank=True, auto_now_add=True)
    update_date = models.DateTimeField(u'修改日期', blank=True, auto_now=True)
class Asset(models.Model):
    assetno = models.CharField(max_length=32)
    asset_type_choices = (
        ('server', u'服务器'),
        ('switch', u'交换机'),
        ('router', u'路由器'),
        ('firewall', u'防火墙'),
        ('storage', u'存储设备'),
        ('NLB', u'F5'),
        ('wireless', u'无线AP'),
        ('others', u'其它类'),
    )
    asset_type = models.CharField(u'资产类型',choices=asset_type_choices, max_length=64, default='server')
    sn = models.CharField(u'资产SN号', max_length=128)
    servermodel=models.CharField(u'资产型号',max_length=64)
    business_ip = models.GenericIPAddressField(u'管理IP', blank=True, null=True)
    #trade_date = models.DateField(u'购买时间', null=True, blank=True)
    expire_date = models.DateField(u'过保日期', null=True, blank=True)
    #price = models.FloatField(u'价格', null=True, blank=True)
    business_unit_choices=((1,'product'),
                           (2,'bete'),
                           (3,'cn|test'),
                           (4,'other'))
    business_unit = models.SmallIntegerField(u'生产环境',choices=business_unit_choices,default=1)
    tags = models.CharField(u'资产标记',blank=True, max_length=128)
    admin = models.ForeignKey(User, verbose_name=u'资产管理员', null=True, blank=True)
    idc = models.ForeignKey(IDC,verbose_name=u'IDC杋房', null=True, blank=True)
    idc_cabinet = models.CharField(u'机柜号',max_length=32)
    create_type_choices=((1,u'人工'),
                         (2,u'自动'))
    create_type=models.SmallIntegerField(choices=create_type_choices,verbose_name=u'数据方式',default=2)
    #marker= models.TextField(u'备注', null=True, blank=True)
    status_type_choices = ((1, u'在线'),
                           (2, u'下线'))
    asset_status=models.SmallIntegerField(choices=status_type_choices,verbose_name=u'状态',default=1)
    reason=models.CharField(max_length=128,null=True)
    release_date=models.DateField(null=True,max_length=32)
    create_date = models.DateTimeField(u'创建日期',blank=True, auto_now_add=True)
    update_date = models.DateTimeField(u'修改日期',blank=True, auto_now=True)

    class Meta:
        verbose_name = '资产总表'
        verbose_name_plural = "资产总表"

    def __unicode__(self):
        return 'asset:%s' % self.assetno

class Server(models.Model):
    asset=models.OneToOneField(Asset)
    #os_type=models.CharField(u'系统类型',max_length=32)
    osrelease=models.CharField(u'系统版本',max_length=64)
    bip = models.GenericIPAddressField(u'业务IP', max_length=64)
    rip = models.GenericIPAddressField(u'管理IP', max_length=64, default='0.0.0.0')
    uptime=models.CharField(u'运行时长',max_length=64)
    users=models.CharField(max_length=64)
    create_date = models.DateTimeField(u'创建日期',blank=True, auto_now_add=True)
    update_date = models.DateTimeField(u'修改日期',blank=True, auto_now=True)

class Cpu(models.Model):
    server=models.ForeignKey(Server)
    cpumodel = models.CharField(u'cpu型号',max_length=64)
    cpucount = models.SmallIntegerField(u'cpu个数')
    cpucorecount=models.SmallIntegerField(u'cpu核心数')
    create_date = models.DateTimeField(u'创建日期',blank=True, auto_now_add=True)
    update_date = models.DateTimeField(u'修改日期',blank=True, auto_now=True)

class Disk(models.Model):
    server = models.ForeignKey(Server)
    disktotalsize=models.CharField(u'磁盘大小',max_length=32)
    diskcount=models.SmallIntegerField(u'磁盘个数')
    diskraid=models.CharField(u'RAID',max_length=32)
    df=models.TextField(null=True)
    create_date = models.DateTimeField(u'创建日期',blank=True, auto_now_add=True)
    update_date = models.DateTimeField(u'修改日期',blank=True, auto_now=True)

class Memory(models.Model):
    server = models.ForeignKey(Server)
    memorycount=models.SmallIntegerField(u'内存个数')
    memorysizeper=models.CharField(u'单条内存大小',max_length=32)
    memorytotal=models.CharField(u'内存总大小',max_length=32)
    memory_slot_count = models.CharField(u'内存插槽个数',max_length=32)
    create_date = models.DateTimeField(u'创建日期',blank=True, auto_now_add=True)
    update_date = models.DateTimeField(u'修改日期',blank=True, auto_now=True)

class Services(models.Model):
    server = models.ForeignKey(Server)
    name=models.TextField(u'应用名称')
    crontab=models.TextField()









