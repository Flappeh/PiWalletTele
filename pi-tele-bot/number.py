

number = []

with open('./data/phone_number.txt','r') as f:
    lines = f.readlines()
    for i in lines:
        num = i.split(':')
        number.append(num[1].strip())

with open('./data/phone_fixed.txt','w') as f:
    for i in number:
        f.write(f"{i}\n")