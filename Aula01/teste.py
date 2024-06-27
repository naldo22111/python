import os
# Obter Dados do Usuario
ipv4_string = input("Informe o prefixo IPv4:")

# Tratamento dos Dados
ipv4_list = ipv4_string.split("/")
ipv4_address = ipv4_list[0]
prefix = ipv4_list[1]

# NetMask
subnet_bits = 32 - int(prefix)
mask = 256 - (2**subnet_bits) 

# Separar os octetos
octects_list = ipv4_address.split(".")
octect_host = int(octects_list[3])
net_address = octect_host & mask
net_address
fixed_portion = f"{'.'.join(octects_list[0:3])}."

# Broadcast Address
broadcast = net_address + (2**subnet_bits)-1

# Retornar os Endereços de Rede e Broadcast
print(f"O endereço de Rede do IP {ipv4_string} é: {fixed_portion}{net_address}") 
print(f"O endereço de Broadcast do IP {ipv4_string} é: {fixed_portion}{broadcast}")



# Executar o Ping
for i in range(1,(2**subnet_bits)-1):
    os.system(f"ping -c 2 {fixed_portion}{net_address+i}")