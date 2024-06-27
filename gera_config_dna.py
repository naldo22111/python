import os
import re
from time import sleep
from datetime import datetime

with open("get_cli_napalm.py") as np:
    exec(np.read())
sleep(3)
folder = r'C:\TFTP-Root'
files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
# print(files)
for f in files:
    file_path = os.path.join(folder, f)
    with open(file_path, 'r') as arquivo:
        file = arquivo.read()
        #
        # Extrair hostname e endereço IP
        hostname_match = re.search(r'hostname (.*)', file)
        hostname = hostname_match.group(1) if hostname_match else None
        sfile_path = os.path.join(folder, f'{hostname}-{datetime.now():%d-%m-%Y-%H-%M-%S}.txt')
        string_to_match = re.compile(r' (access|voice) vlan (\d+)')
        vlans_match = re.finditer(string_to_match,file)
        #
        vlans_list = []
        vlan_list = []
        for vlan_match in vlans_match:
            if vlan_match.group(2) not in vlans_list:
                vlans_list.append(vlan_match.group(2))
        for vlan in vlans_list:
                vlan_name = re.search(rf'{vlan} +([\S]+)\s+active',file)
                # sleep(0.5)
                vlan_list.append({'vlan_id':vlan,
                                  'vlan_name':vlan_name.group(1)})
                sleep(1)
        with open(sfile_path, 'w') as f:
            print('vlan 99\n name Gerencia_Switchs\n!',file=f)
            for vlan in vlan_list:
                print(f'vlan {vlan['vlan_id']}', file=f)
                print(f' name {vlan['vlan_name']}\n!', file=f)
        #
            string_to_match = re.compile(r"interface GigabitEthernet(\d\/)+\d+\n")
            interfaces_match = re.finditer(string_to_match, file)
            #
            qtde = len(re.findall(r"provision ws",file))
            match qtde:
                case 1:
                    ten1_str = re.compile(r"(Giga.*1\/\d\/4[1-8])")
                    tenn_str = None
                case _:
                    ten1_str = re.compile(r"(Giga.*1\/\d\/4[1-8])")
                    tenn_str = re.compile(rf"(Giga.*{qtde}\/\d\/4[1-8])")
            #        
            for interface in interfaces_match:
                # with open(sfile_path, 'a') as f:
                    remover = re.compile(r"Gi.*\d+\/\d+\/(49|50)|Ten.*")
                    if re.search(remover,interface.group()):
                        continue
                    if ten1_str.search(interface.group()):
                        aps_1 = re.sub(ten1_str,rf"Ten{ten1_str.search(interface.group()).group()}",interface.group()).replace('\n', '')
                        print(aps_1,file=f)
                    elif tenn_str and tenn_str.search(interface.group()):
                        aps_n = re.sub(tenn_str,rf"Ten{tenn_str.search(interface.group()).group()}",interface.group()).replace('\n', '')
                        print(aps_n,file=f)       
                    else:
                        print(interface.group().replace('\n', ''),file=f)
                    end_ident = re.compile("!").search(file,interface.end()+1).end()
                    ident_parse = file[interface.end():end_ident].splitlines()
                    for line in ident_parse:
                        if line.startswith(" description"):
                            print(line, file=f)
                        switchport_re = re.search('switchport.*', line)
                        if switchport_re:
                            user_vlan_match = re.search(r'access vlan (\d+)',line)
                            not_user_vlan = int(user_vlan_match.group(1)) if user_vlan_match else None
                            # if "vlan 55" in line:
                            if not_user_vlan and (not_user_vlan > 14):
                                print(f' {switchport_re.group()}',file=f)
                                print(' switchport mode access',file=f)
                                break
                            else:
                                print(f' {switchport_re.group()}',file=f)
                    print(r""" storm-control broadcast level 3.00
 storm-control multicast level 3.00
 spanning-tree portfast
!""",file=f)