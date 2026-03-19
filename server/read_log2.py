with open('server.log', 'r', encoding='gbk', errors='ignore') as f:
    lines = f.readlines()
    print(''.join(lines[-100:]))
