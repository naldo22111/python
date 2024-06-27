import re
from tabulate import tabulate
#
file_path = r'C:\TFTP-Root\M270301'

# Read the contents of the file into a variable
with open(file_path, 'r') as file:
    file_content = file.read()
    file_content = file_content.replace(' --More--         ','')

# Split the output into individual lines
lines = file_content.replace(", ","\n").splitlines()

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
        if vlan and (int(vlan) < 15) and not voice:
            # Update the most recent row in the data list with the mismatch
            erro = 'Falta Vlan de Voz'
            data[-1]["Mismatch"] = erro

# Convert the parsed data into a DataFrame
print (tabulate(data, headers="keys"))