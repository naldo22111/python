ipv4_string = input("Informe o prefixo IPv4:")
ipv4_list = ipv4_string.split("/")
ipv4_address = ipv4_list[0]
prefix = ipv4_list[1]

# NetMask
subnet_bits = 32 - int(prefix)
mask = 256 - (2**subnet_bits) 

# Separar os octetos
octetos = ipv4_address.split(".")
octect_host = int(octetos[3])
octect_host
# fixed_portion = '.'.join(octetos[0:3])

# Net & Broadcast Address
net_address = octect_host & mask
broadcast = net_address + (2**subnet_bits)-1

# Apresentando o resultado
print(f"O endereço de rede é: {'.'.join(octetos[0:3])}.{net_address}")
print(f"O endereço de broadcast é: {'.'.join(octetos[0:3])}.{broadcast}")

# Teste de Ping
import os
os.system(f"ping -c 3 {'.'.join(octetos[0:3])}.{net_address+1}")