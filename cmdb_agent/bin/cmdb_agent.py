#!/usr/bin/env python
# -*-coding:utf-8-*-
import  urllib, httplib, json, urllib2,os,sys,logging
import collection
from optparse import OptionParser
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from conf import setting
from collections import Mapping,Iterable
logging.basicConfig(filename='../logs/log.log', format='%(asctime)s - %(name)s - %(levelname)s -%(module)s:  %(message)s',datefmt='%Y-%m-%d %H:%M:%S %p',level=logging.INFO)
def color_print(msg, color='red', exits=False):
    """
    Print colorful string.
    颜色打印字符或者退出
    """
    color_msg = {'blue': '\033[1;36m%s\033[0m',
                 'green': '\033[1;32m%s\033[0m',
                 'yellow': '\033[1;33m%s\033[0m',
                 'red': '\033[1;31m%s\033[0m',
                 'title': '\033[30;42m%s\033[0m',
                 'info': '\033[32m%s\033[0m'}
    msg = color_msg.get(color, 'red') % msg
    print msg
    if exits:
        time.sleep(2)
        sys.exit()
    return msg
class Handle(object):
    def __init__(self,data,url):
        self.data=data#collection.CollectInfo().collect()
        self.url=url#"http://%s:%s/%s/"%(setting.CMDB_Server['ip'],setting.CMDB_Server['port'],setting.CMDB_Server['url'])
    def postdata(self):
        if os.path.exists('%s/conf/.asset'%os.path.dirname(os.path.dirname(os.path.abspath(__file__)))):
            if self.comparedict():
                logging.info("the asset for this server  no change")
                color_print('the asset for this server no change ...','info')
            else:
                with open('%s/conf/.asset' % (os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'r') as oldf:
                    data_dic = json.loads(oldf.read().strip())
                self.data.update({'update':'yes'})
                self.data.update({'asset_id':data_dic.pop('asset_id')})
                self.handlerurl()
        else:
            self.handlerurl()

    def handlerurl(self):
        try:
            data = json.dumps(self.data)
            jdata = urllib.urlencode({'data': data})
            req = urllib2.Request(self.url, jdata)
            res = urllib2.urlopen(req)
            ret_data = json.loads(res.read())
            if ret_data.get('asset_id'):
                self.assetid = ret_data['asset_id']
                self.data.update({'asset_id': self.assetid})
                with open('%s/conf/.asset' % (os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'w') as f:
                    f.write(json.dumps(self.data))
                    logging.info('conf/.asset  file updated')
                color_print('submit success..........[ok]','green')
                logging.info("the asset for  this server has changed and posted the server")
            res.close()
        except Exception  as e:
            logging.error('Error:  %s'%e)

    def comparedict(self):
        if (os.path.exists('%s/conf/.asset' % (os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))):
            with open('%s/conf/.asset' % (os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'r') as oldf:
                data_dic=json.loads(oldf.read().strip())
                if data_dic.has_key('update'):
                    data_dic.pop('update')
                if data_dic.has_key('asset_id'):
                    data_dic.pop('asset_id')
            ret_cmp=cmp(self.convert(data_dic),self.data)
            if ret_cmp==0:
                return True
            else:
                return False

    def convert(self,data):
        if isinstance(data,basestring):
            return str(data)
        elif isinstance(data, Mapping):
            return dict(map(self.convert, data.iteritems()))
        elif isinstance(data, Iterable):
            return type(data)(map(self.convert, data))
        else:
            return data
if __name__ == '__main__':
    usage='Usage:%prog [options] arg1 arg2 ...'
    parser=OptionParser(usage,version='%prog 1.0')
    parser.add_option("-r","--force",action="store_true",dest='verbose',help="force update when asset information for  this server delete from db..")
    parser.add_option("-f", "--file", action="store",dest="filename",metavar="FILE",help="write asset information for this server to file..")
    (options,args)=parser.parse_args()
    if options.verbose:
        info=raw_input('please confirm asset for this server has deleteed from db..[ y|n ]:')
        if info.strip().upper()=="Y":
            os.system('rm -f %s/conf/.asset' % (os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            Handle(collection.CollectInfo().collect(),"http://%s:%s/%s/"%(setting.CMDB_Server['ip'],setting.CMDB_Server['port'],setting.CMDB_Server['url'])).postdata()
    elif options.filename:
        with open('%s' %options.filename,'w')  as f:
            f.write(json.dumps(collection.CollectInfo().collect()))
    else:
        Handle(collection.CollectInfo().collect(), "http://%s:%s/%s/" % (setting.CMDB_Server['ip'], setting.CMDB_Server['port'], setting.CMDB_Server['url'])).postdata()



