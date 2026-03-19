with open('server.log', 'r', encoding='gbk', errors='ignore') as f:
    content = f.read()
    idx = content.rfind('Traceback')
    if idx != -1:
        print(content[idx:])
    else:
        print("No traceback found in log.")
