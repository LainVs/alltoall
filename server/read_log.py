with open('server.log', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    print(''.join(lines[-50:]))
