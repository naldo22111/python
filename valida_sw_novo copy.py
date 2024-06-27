from napalm import get_network_driver
from tabulate import tabulate
import re
driver = get_network_driver('ios')
devices = ['M270401', 'M270301']
username = 'pavezi'
passwd = 'Wiseit@2023###'


for sw in devices:
    device = driver(sw,username,passwd,optional_args = {'secret':'Wiseit@2023###', 'fast_cli':False,'inline_transfer':True},)
    device.open()
    dados = device.cli(['show interfaces switchport'])
    for command, output in dados.items():
        vlans_dados = output
        # Split the output into individual lines
        lines = vlans_dados.splitlines()

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
                if vlan and (int(vlan) > 1 and int(vlan) < 15) and not voice:
                    # Update the most recent row in the data list with the mismatch
                    erro = 'Falta Vlan de Voz'
                    data[-1]["Mismatch"] = erro

        # Tabulates the content
        print (f'verificado no SW: {sw}\n\n{tabulate(data, headers="keys")}')
    device.close()