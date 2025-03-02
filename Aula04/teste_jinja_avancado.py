from jinja2 import Template
import csv


with open('site_vlans.csv') as f:
    reader = csv.DictReader(f)
    ######  Renderizacao do Template Jinja2
    
print (reader)
    for row in reader:
        interface_config = interface_template.render(
            interface = row['Interface'],
            vlan = row['Vlan'],
            host = row['Host'],
            connection = row['Connection']
        )
        interface_configs += interface_config
