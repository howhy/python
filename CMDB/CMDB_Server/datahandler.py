#!/usr/bin/env python
#-*-coding:utf-8-*-
import models,datetime,logging
logger=logging.getLogger('cmdb.views')
class DataHandler(object):
    def __init__(self,postdata):
        self.data=postdata
        self.assetid=''
    def datahandler(self):
        try:
            if self.data.get('asset_id'):
                if self.data.get('update'):
                    asset_obj= models.Asset.objects.filter(id=self.data.get('asset_id'))
                    if asset_obj:##客户端有更新
                        asset_obj.update(assetno=self.data['assetno'], asset_type=self.data['asset_type'], sn=self.data['sn'], servermodel=self.data['model'],release_date=datetime.datetime.strptime(self.data['release date'],'%m/%d/%Y').strftime('%Y-%m-%d'), business_ip=self.data['ip'],business_unit=self.judgeIDC(self.data['ip']),idc_id=self.judgeIDC(self.data['ip']))
                        server_obj=models.Server.objects.filter(asset=asset_obj)
                        server_obj.update(osrelease=self.data['os_release'])
                        models.Cpu.objects.filter(server=server_obj).update(cpumodel=self.data['cpu']['cpu_model'],cpucount=self.data['cpu']['cpu_count'],cpucorecount=self.data['cpu']['cpu_core_count'])
                        models.Disk.objects.filter(server=server_obj).update( disktotalsize=self.data['disk']['Size1'],diskcount=self.data['disk']['Number Of Drives1'],diskraid=self.data['disk']['RAID Level1'],df='%s%s'%(u" 文件系统                 容量  已用  可用 已用% 挂载点\n",self.data['disk']['df']))
                        if self.data['disk'].get('Size2'):
                            models.Disk.objects.filter(server=server_obj).update( disktotalsize=self.data['disk']['Size2'], diskcount=self.data['disk']['Number Of Drives2'], diskraid=self.data['disk']['RAID Level2'])
                        if self.data['disk'].get('Size3'):
                            models.Disk.objects.filter(server=server_obj).update(disktotalsize=self.data['disk']['Size3'], diskcount=self.data['disk']['Number Of Drives3'], diskraid=self.data['disk']['RAID Level3'])
                        models.Memory.objects.filter(server=server_obj).update( memorycount=self.data['memory']['mem_count'],memorysizeper=self.data['memory']['mem_size_per'], memorytotal=self.data['memory']['mem_total'],memory_slot_count=self.data['memory']['mem_slot_count'])
                    else:## 数据库已删除但客户端有更新时
                        asset_obj = models.Asset(assetno=self.data['assetno'], asset_type=self.data['asset_type'], sn=self.data['sn'],servermodel=self.data['model'],release_date=datetime.datetime.strptime(self.data['release date'],'%m/%d/%Y').strftime('%Y-%m-%d'), business_ip=self.data['ip'],business_unit=self.judgeIDC(self.data['ip']),idc_id=self.judgeIDC(self.data['ip']))
                        asset_obj.save()
                        self.serverhandler(asset_obj)
                    logger.info('IP:%s successfully update asset data,assetid:%s' % (self.data['ip'], self.data.get('asset_id')))
                self.assetid=self.data.get('asset_id')
            else:
                asset_obj = models.Asset(assetno=self.data['assetno'], asset_type=self.data['asset_type'], sn=self.data['sn'], servermodel=self.data['model'],release_date=datetime.datetime.strptime(self.data['release date'],'%m/%d/%Y').strftime('%Y-%m-%d'), business_ip=self.data['ip'],business_unit=self.judgeIDC(self.data['ip']),idc_id=self.judgeIDC(self.data['ip']))
                asset_obj.save()
                self.assetid = asset_obj.id
                self.serverhandler(asset_obj)
                logger.info('IP:%s successfully sumbit asset data,assetid:%s' % (self.data['ip'], asset_obj.id))
        except Exception as e:
            logger.error(e.message)
    def judgeIDC(self,ipadd):
        try:
            if ipadd.startswith('172.16.32') or ipadd.startswith('172.24.32'):
                businessunit = 1
            elif ipadd.startswith('192.168.11'):
                businessunit = 2
            elif ipadd.startswith('172.16.1') or ipadd.startswith('172.16.2'):
                businessunit = 3
            else:
                businessunit = 4
            return businessunit
        except Exception as e:
            logger(e.message)

    def serverhandler(self,asset):
        try:
            if asset.id:
                if self.data['ip'].startswith('172.'):
                    server_rip = self.data['ip'].replace('172.', '10.')
                else:
                    server_rip='0.0.0.0'
                server_obj=models.Server(asset=asset,osrelease=self.data['os_release'],uptime=self.data['uptime'],users=self.data['users'],bip=self.data['ip'],rip=server_rip)
                server_obj.save()
                self.cputhandler(server_obj)
                self.diskhandler(server_obj)
                self.memoryhandler(server_obj)
                self.servicehandler(server_obj)
        except Exception as e:
            logger.error(e.message)

    def cputhandler(self,server):
        if server.id:
            cpu_obj=models.Cpu(server=server,cpumodel=self.data['cpu']['cpu_model'],cpucount=self.data['cpu']['cpu_count'],cpucorecount=self.data['cpu']['cpu_core_count'])
            cpu_obj.save()

    def diskhandler(self,server):
        if server.id:
            models.Disk.objects.create(server=server,disktotalsize=self.data['disk']['Size1'], diskcount=self.data['disk']['Number Of Drives1'],diskraid=self.data['disk']['RAID Level1'],df='%s%s'%(u" 文件系统                容量  已用  可用 已用% 挂载点\n",self.data['disk']['df']))
            if self.data['disk'].get('Size2'):
                models.Disk.objects.create(server=server, disktotalsize=self.data['disk']['Size2'],diskcount=self.data['disk']['Number Of Drives2'], diskraid=self.data['disk']['RAID Level2'])
            if self.data['disk'].get('Size3'):
                models.Disk.objects.create(server=server, disktotalsize=self.data['disk']['Size3'],diskcount=self.data['disk']['Number Of Drives3'], diskraid=self.data['disk']['RAID Level3'])

    def memoryhandler(self,server):
        if server.id:
            models.Memory.objects.create(server=server,memorycount=self.data['memory']['mem_count'], memorysizeper=self.data['memory']['mem_size_per'],memorytotal=self.data['memory']['mem_total'],memory_slot_count=self.data['memory']['mem_slot_count'])
    def servicehandler(self,server):
        if server.id:
           models.Services.objects.create(server=server,name=self.data['serviceinfo'],crontab=self.data['crontab'])