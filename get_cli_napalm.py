from napalm import get_network_driver
driver = get_network_driver('ios')
devices = ['M131301', 'M131401']
username = 'pavezi'
passwd = 'Wiseit@2023###'


for sw in devices:
    device = driver(sw,username,passwd,optional_args = {'secret':'Wiseit@2023###', 'fast_cli':False,'inline_transfer':True},)
    device.open()
    dados = device.cli(['terminal le 0', 'show running','show cdp neigh','show vlan brief', 'show interfaces switchport','show interfaces status','show mac add dynamic | exc Po'])
    with open(rf'C:\TFTP-Root\{sw}','w') as f:
        for command, output in dados.items():
         print(command, file=f)
         print ("\n".join(output.split('\n')),file=f)
    device.close()