import config
import socket
import time

cache_table = { }
cache_ptr = 0

def insert_cache_value(request, info):
    global cache_table
    global cache_ptr

    if cache_ptr >= config.CACHE_TABLE_SIZE:
        for i in cache_table:
            if min_timestamp > cache_table[i]['timestamp']:
                min_timestamp = cache_table[i]['timestamp']
                position = i
    else:
        position = cache_ptr
        cache_ptr = cache_ptr + 1

    cache_table[position] = { 'key' : request, 'value' : info, 'timestamp': time.time() }

def get_cache_value(request):
    for i in cache_table:
        if cache_table[i]['key'] == request:
            if cache_table[i]['timestamp'] <= time.time() - config.CACHE_EXPIRATION_TIME:
                return cache_table[i]['value']

    return None

def print_cache():
    print('REQUEST - INFO - TIMESTAMP')

    for i in cache_table:
        if cache_table[i]['timestamp'] <= time.time() - config.CACHE_EXPIRATION_TIME:
            print(cache_table[i]['key'] + ' - ' + cache_table[i]['value'] + ' - ' + str(cache_table[i]['timestamp']))

# Cria o socket do cliente
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Realiza a conexao com o servidor
s.connect((config.SERVER_HOST, config.SERVER_PORT))

while 1:
    entry = input('> ')

    if entry[0] == '/':
         if entry[1:] == 'cache':
             print_cache()
         elif entry[1:] == 'exit':
             exit(0)
         else:
             print('Unknown command: ' + entry[1:])
    else:
        info = get_cache_value(entry)

        if info is None:
            # Envia requisicao
            s.send(entry.encode('utf8'))
            info = s.recv(config.MAX_INFO_LENGTH).decode('utf8')

            # Salva na cache
            insert_cache_value(entry, info)

        print(info)
