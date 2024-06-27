from napalm import get_network_driver
from tabulate import tabulate
import re
from datetime import datetime
import logging



driver = get_network_driver('ios')
username = 'cgabriel'
passwd = 'Ghosana@2024'

#### Funtcion to validade Match Between Data Vlan and Voice Vlan
def is_match(data,voice):
    vlan_pair = [{'3':'110'},{'7':'111'},{'8':'113'},{'9':'114'},{'10':'115'},{'11':'116'},{'12':'112'}]
    for dict in vlan_pair:
        if data in dict and dict[data] == voice:
            break
    else:
        return 'Vlan de Voz/Dados fora do Padrão'


def valida_voz(lines):
    # Initialize an empty list to store the parsed data
    data = []

    # Initialize variables to store temporary values
    name = None
    vlan = None
    voice = None
    erro = None
    # Iterate over each line
    for line in lines:
        # Check if the line starts with "NAME:" (indicating a new device)
        if line.startswith("Name:"):
            # Extract the device name
            name = line[5:].strip()
            data.append({
                "Interface": name,
                "Vlan Dados": None,
                "Vlan Voz": None,
                "Mismatch": None
            })
        # Check if the line starts with "VLAN:" (indicating a part number)
        elif line.startswith("Access"):
            # Update the most recent row in the data list with the part number
            vlan_match = re.search(r'Access.*:\s(\d+)',line)
            vlan = vlan_match.group(1)
            data[-1]["Vlan Dados"] = vlan
        # Check if the line starts with "Voice:" (indicating a description)
        elif line.startswith("Voice"):
            # Update the most recent row in the data list with the description
            voice_match = re.search(r'Voice.*:\s(\d+)',line)
            voice = voice_match.group(1) if voice_match else None
            data[-1]["Vlan Voz"] = voice
            # Check if data vlan is less then 15 and there is no voice vlan (indicating mismatch)
            if vlan and (int(vlan) > 1 and int(vlan) < 13):
                if not voice:
                    # Update the most recent row in the data list with the mismatch
                    erro = 'Falta Vlan de Voz'
                    
                else:
                    erro = is_match(vlan,voice)
                data[-1]["Mismatch"] = erro

    # Tabulates the content
    print (f'\n{'-'*50}\nVerificado no SW: {sw}...\n\n{tabulate(data, headers="keys")}\n\n\n')
    logging.info(f'\n{'-'*50}\nVerificado no SW: {sw}...\n\n{tabulate(data, headers="keys")}\n\n\n')


#### validador Endereços MAC
#
def verify_mac(lines,mac_string,vlan_id):
    data = []
    print(f'\n\nVerificando MACs iniciando com {mac_string} na vlan {vlan_id}...')
    logging.info(f'Verificando MACs iniciando com {mac_string} na vlan {vlan_id}...')

    # Iterate over each line
    count = 0
    for line in lines:
        
        # Check if the line contains "Port_channel" (indicating remote MAC Address)
        # print(line)
        if 'Po' in line:
            continue
        # Check if the line contains "849a:" (Vlan 52)
        elif mac_string in line:
            if '#' in line:
                continue
            else:
                count +=1
                # Check if the mac is on correct vlan
                vlan_match = re.search(r'\s+(\d+)',line)
                vlan = vlan_match.group(1)
                mac = re.search(r'((\w{4}\.){2}\w{4})',line)
                name = re.search(r'DYNAMIC\s+(\S+)',line)
                data.append({'mac-address':mac.group(1),
                            'vlan':vlan,
                            'porta':name.group(1),
                            'status':None})
                if vlan != vlan_id:
                    data[-1]['status']='NOK'                    
                    # print(f'O Mac {mac.group(1)} na porta {name.group(1)}, está na Vlan ERRADA!!! ({vlan})')
                    # logging.info(f'O Mac {mac.group(1)} na porta {name.group(1)}, está na Vlan ERRADA!!! ({vlan})')
                else:
                    data[-1]['status']='OK'
                    # print(f'O MAC {mac.group(1)} encontrado na vlan {vlan} está correto!!!')
                    # logging.info(f'O MAC {mac.group(1)} encontrado na vlan {vlan} está correto!!!')
    if count == 0:
        print (f'Nenhum Mac iniciado em {mac_string} da vlan {vlan_id} foi encontrado neste switch!')
        logging.info (f'Nenhum Mac iniciado em {mac_string} da vlan {vlan_id} foi encontrado neste switch!')
    # Tabulates the content
    print (f'\n\n {count} macs encontrados no SW: {sw}...\n\n{tabulate(data, headers="keys")}\n{'-'*50}')
    logging.info(f'\n\n {count} macs encontrados no SW: {sw}...\n\n{tabulate(data, headers="keys")}\n{'-'*50}')



if __name__ == '__main__':
    devices = ['M121601']
    

    for sw in devices:
        # Configure logging to save to a file
        logging.basicConfig(filename=rf'C:\TFTP-Root\Check-{sw}-{datetime.now():%d-%m-%Y-%H-%M-%S}.txt', level=logging.INFO)

        logging.info(f'#'*80)
        logging.info(f'Iniciando verificação no {sw}...')
        print(f'#'*80)
        print(f'Iniciando verificação no {sw}...')
        device = driver(sw,username,passwd,optional_args = {'secret':'Ghosana@2024', 'fast_cli':False,'inline_transfer':True},)
        device.open()
        dados = device.cli(['show platform','show interfaces switchport','show mac add dynamic', 'show environment power', 'show cdp nei'])
        for command, output in dados.items():
            if command == 'show interfaces switchport':
                vlans_dados = output
            elif command =='show mac add dynamic':
                macs_dados = output
            else:
                logging.info(f'\n{command}\n{'-'*35}\n\n{output}')
                print(f'\n{command}\n{'-'*35}\n\n{output}')

        # Split the output into individual lines
        lines_voz = vlans_dados.splitlines()
        lines_macs = macs_dados.splitlines()

        logging.info('\nshow interfaces switchport')
        logging.info('\n'.join(lines_voz))
        logging.info('\nshow mac add dynamic')
        logging.info('\n'.join(lines_macs))

        # Execut Voice Validation
        valida_voz(lines_voz)

        vlan_pair = [{'mac':'849a', 'vlan':'52'},
                {'mac':'c828', 'vlan':'55'},
                {'mac':'0050', 'vlan':'85'}, #
                {'mac':'001a', 'vlan':'113'}, # voice vlan
                {'mac':'60c7', 'vlan':'8'},
                {'mac':'8425', 'vlan':'8'},
                {'mac':'0002', 'vlan':'8'},
                {'mac':'50b3', 'vlan':'8'},
                {'mac':'641c', 'vlan':'8'},
                {'mac':'6c41', 'vlan':'8'},
                {'mac':'74e6', 'vlan':'8'},
                {'mac':'8425', 'vlan':'8'},
                {'mac':'c8cb', 'vlan':'8'},
                {'mac':'8469', 'vlan':'8'},
                ]
        for pair in vlan_pair:
            verify_mac(lines_macs,pair['mac'], pair['vlan'])

        device.close()
    
    print(f'\n{'-'*35}\nVerificação Concluida!')
    logging.info(f'\n{'-'*35}\nVerificação Concluida!')