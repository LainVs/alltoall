import codecs
with codecs.open('server.log', 'r', encoding='gbk', errors='ignore') as f:
    content = f.read()
    idx = content.rfind('Traceback')
    with codecs.open('tb.txt', 'w', encoding='utf-8') as out:
        if idx != -1:
            out.write(content[idx:])
        else:
            out.write("No traceback found in log.")
