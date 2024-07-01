#### Aula 04 - Jinja2

import jinja2
import csv
from napalm import get_network_driver

##### Definição das Variáveis Iniciais

source_file = 'switch-ports.csv'
interface_template_file = 'switch-interface-template.j2'
interface_configs=''


with open(interface_template_file) as f:
    interface_template = jinja2.Template(f.read(),keep_trailing_newline=True)
    
with open(source_file) as f:
    reader = csv.DictReader(f)
    for row in reader:
        interface_config = interface_template.render(
            interface = row['Interface'],
            vlan = row['Vlan'],
            host = row['Host'],
            connection = row['Connection']
        )
        interface_configs += interface_config


with open ('interface_configs.txt','w') as f:
    f.write(interface_configs)
    

config_set = interface_configs.split('\n')
print(config_set)

driver = get_network_driver('nxos_ssh')
devices = ['sbx-nxos-mgmt.cisco.com']
username = 'admin'
passwd = 'Admin_1234!'
device = driver('sbx-nxos-mgmt.cisco.com',username,passwd)
device.open()
device.load_merge_candidate(filename='interface_configs.txt')
print("\nDiff:")
print(device.compare_config())

# You can commit or discard the candidate changes.
try:
    choice = raw_input("\nWould you like to commit these changes? [yN]: ")
except NameError:
    choice = input("\nWould you like to commit these changes? [yN]: ")
if choice == "y":
    print("Committing ...")
    device.commit_config()
else:
    print("Discarding ...")
    device.discard_config()

# close the session with the device.
device.close()
print("Done.")