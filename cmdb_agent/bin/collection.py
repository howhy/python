#!/usr/bin/env python
# -*-coding:utf-8-*-
import os, sys, commands, stat,locale
class CollectInfo(object):
    def __init__(self):
        pass
    def collect(self):
        filter_keys = ['Manufacturer', 'Serial Number', 'Product Name']
        systeminfo = {}
        for key in filter_keys:
            try:
                cmd_res = commands.getoutput("dmidecode -t 1 | grep '%s'" % key)
                res_to_list = cmd_res.strip().split(':')
                if len(res_to_list) > 1:
                    systeminfo[key] = res_to_list[1].strip()
                else:
                    systeminfo[key] = 'null'
            except Exception as e:
                systeminfo[key] = 'dmidecode -t 1 is wrong'
        data = {"asset_type": 'server'}
        data['model'] = systeminfo['Manufacturer'].split(' ')[0] + systeminfo['Product Name'] or 'OEM'
        data['sn'] = systeminfo['Serial Number']
        data['release date']=commands.getoutput("dmidecode | grep 'Release Date'").strip().split(':')[1].strip()
        data.update(self.cpuinfo())
        data.update(self.osinfo())
        data.update(self.meminfo())
        data.update(self.diskinfo())
        data.update(self.ipinfo())
        data.update(self.services())
        return data


    def osinfo(self):
        osinfo_cmd = 'cat /etc/redhat-release'
        os_release = commands.getoutput(osinfo_cmd)
        users_cmd="cat /etc/passwd | awk -F: '{if ($3>999) print $1}'"
        users=commands.getoutput(users_cmd)
        uptime=commands.getoutput("uptime |awk '/days/{print $3}'")
        hostname=commands.getoutput('hostname')
        osinfo = {'os_release': os_release,'assetno':hostname,"users":users,"uptime":uptime}
        return osinfo
    def services(self):
        services_cmd="ss -tnap | awk -F'[:,]+' '/LISTEN/{print $2 $4}' | tr '*(\"' ' '|tr -s [:space:]"
        services_list=commands.getoutput(services_cmd).strip()
        crontab=commands.getoutput("crontab -l")
        servicesinfo={'serviceinfo':services_list,'crontab':crontab}
        return servicesinfo

    def cpuinfo(self):
        cpu_info_cmd = 'cat /proc/cpuinfo'
        raw_data = {
            'cpu_model': "%s |grep 'model name' |head -1 " % cpu_info_cmd,
            'cpu_count': "%s |grep  'processor'|wc -l " % cpu_info_cmd,
            'cpu_core_count': "%s |grep 'cpu cores' |awk -F: '{SUM +=$2} END {print SUM}'" % cpu_info_cmd,
        }
        for k, cmd in raw_data.items():
            try:
                cmd_res = commands.getoutput(cmd)
                raw_data[k] = cmd_res.strip() or 'null'
            except Exception as e:
                raw_data[k] = 'cpuinfo fail'
        cpu_info = {
            "cpu_count": raw_data["cpu_count"],
            "cpu_core_count": raw_data["cpu_core_count"]
        }
        cpu_model = raw_data["cpu_model"].split(":")
        if len(cpu_model) > 1:
            cpu_info["cpu_model"] = cpu_model[1].strip()
        else:
            cpu_info["cpu_model"] = -1
        return {'cpu': cpu_info}


    def meminfo(self):
        mem_info = {}
        mem_info_cmd = "dmidecode -t memory | awk -F: '/Number Of Devices/||/Size: [1-9]/{print $2}'"
        mem_ret = commands.getoutput(mem_info_cmd).strip().split('\n')
        mem_info['mem_slot_count'] = mem_ret[0].strip()
        mem_info['mem_size_per'] = mem_ret[1].strip()
        mem_info['mem_count'] = len(mem_ret) - 1
        mem_info['mem_total'] = str(int(mem_ret[1].strip().split(' ')[0]) * (len(mem_ret) - 1) / 1024) + 'G'
        return {'memory': mem_info}


    def diskinfo(self):
        disk_info = {}
        script_path = os.path.dirname(os.path.abspath(__file__))
        os.chmod("%s/MegaCli" % script_path, stat.S_IEXEC)
        disk_cmd = "%s/MegaCli -LDInfo -Lall -aALL | grep 'RAID Level'" % script_path
        disk_cmd_ret = commands.getoutput(disk_cmd).strip()
        if len(disk_cmd_ret) > 0:
            filter_key = ['RAID Level', 'Number Of Drives', 'Size']
            for key in filter_key:
                shell_command = "%s/MegaCli -LDInfo -Lall -aALL | grep '^%s'" % (script_path, key)
                # disk_info[key]=commands.getoutput(shell_command).strip().split(':')[1].strip()
                disk_info_line = commands.getoutput(shell_command).strip().split('\n')
                a = 1
                for line in disk_info_line:
                    if key == 'RAID Level':
                        disk_info[key + str(a)] = 'RAID' + line.split(':')[1].strip().split(',')[0].split('-')[1]
                    else:
                        disk_info[key + str(a)] = line.split(':')[1].strip()
                    a = a + 1
        else:
            disk_cmd = "cat /proc/mdstat | awk -F: '/Personalities/{print $2}'"
            disk_info_cmd = commands.getoutput(disk_cmd).strip("[|]| ")
            disk_total_cmd = "fdisk -l |awk -F[：,] 'NR==2{print $2}'"
            disk_count_cmd = "cat /proc/scsi/scsi | egrep  'Model: ST|Model: WD'|wc -l"
            disk_total = commands.getoutput(disk_total_cmd)
            disk_count = commands.getoutput(disk_count_cmd)
            disk_info = {'Size1': disk_total, 'RAID Level1': disk_info_cmd, 'Number Of Drives1': disk_count}
        disk_info['df']=commands.getoutput("df -h | awk 'NR!=1'").strip() 
        return {'disk': disk_info}


    def ipinfo(self):
        ip_cmd = "ip addr | awk -F\"[ /]+\" '/inet 192.168/||/inet 172.16/||/172.24/||/inet 10.6/{print $3}'"
        ip_addr = commands.getoutput(ip_cmd)
        ip_info = {'ip': ip_addr}
        return ip_info



