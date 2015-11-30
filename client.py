import config
import socket
import time
import datetime

# Tabela cache
cache_table = { }
# Ponteiro da tabela cache
cache_ptr = 0

# Insere uma requisicao na cache
def insert_cache_value(request, info):
    # Usa as variaveis globais de tabela cache e ponteiro
    global cache_table
    global cache_ptr

    # Se o ponteiro ja excedeu o maximo da tabela cache, entao
    # e encontrada a posicao com o menor timestamp para se inserir
    # o valor
    if cache_ptr >= config.CACHE_TABLE_SIZE:
        # Define o menor timestamp como o atual (que, por consequencia,
        # e maior que todos os outros ja existentes na tabela)
        min_timestamp = time.time()

        # Percorre a tabela cache para encontrar o menor timestamp
        for i in cache_table:
            # Se o timestamp encontrado e menor que o menor timestamp
            # atual, entao define-o como menor timestamp e salva sua posicao
            if min_timestamp > cache_table[i]['timestamp']:
                min_timestamp = cache_table[i]['timestamp']
                position = i

    # Se ainda ha posicoes livres, entao armazena a requisicao na posicao
    # definida pelo ponteiro e incrementa o ponteiro
    else:
        position = cache_ptr
        cache_ptr = cache_ptr + 1

    # Altera os valores da tabela na posicao encontrada
    cache_table[position] = { 'key' : request, 'value' : info, 'timestamp': time.time() }

# Verifica se a requisicao esta na cache e retorna seu valor, caso
# nao seja encontrada retorna "None"
def get_cache_value(request):
    # Percorre a tabela cache
    for i in cache_table:
        # Verifica se a chave da entrada condiz com a requisicao e se sua validade nao expirou
        if cache_table[i]['key'] == request and cache_table[i]['timestamp'] > time.time() - config.CACHE_EXPIRATION_TIME:
            # Retorna o valor da entrada
            return cache_table[i]['value']

    # Retorna "None" se nao fora encontrada a entrada
    return None

# Imprime a tabela cache
def print_cache():
    # Imprime cabecalho
    print('REQUEST - INFO - TIMESTAMP')

    # Percorre todas as entradas da tabela
    for i in cache_table:
        # Se a entrada atual nao expirou sua validade
        if cache_table[i]['timestamp'] > time.time() - config.CACHE_EXPIRATION_TIME:
            # Imprime suas informacoes
            print(cache_table[i]['key'] + ' - ' + cache_table[i]['value'] + ' - ' + datetime.datetime.fromtimestamp(cache_table[i]['timestamp']).strftime('%Y-%m-%d %H:%M:%S'))

# Loop principal do programa
while 1:
    # Le entrada do usuario
    entry = raw_input('> ')

    # Se comeca com o caractere '/', entao trata como um comando
    if entry[0] == '/':
         # Comando para imprimir a tabela cache
         if entry[1:] == 'cache':
             print_cache()
         # Comando para sair do programa
         elif entry[1:] == 'exit':
             exit(0)
         # Se o comando nao e conhecido, imprime um erro na tela
         else:
             print('Unknown command: ' + entry[1:])

    # Caso contrario, e uma entrada
    else:
        # Verifica se a entrada esta na tabela cache 
        info = get_cache_value(entry)

        # Se nao estiver, conecta ao servidor para obter sua informacao
        if info is None:
            # Cria o socket do cliente
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Realiza a conexao com o servidor
            s.connect((config.SERVER_HOST, config.SERVER_PORT))

            # Envia requisicao
            s.send(entry.encode('utf8'))

            # Aguarda resposta do servidor
            info = s.recv(config.MAX_INFO_LENGTH).decode('utf8')

            # Salva na cache
            insert_cache_value(entry, info)

        # Imprime informacao para o usuario 
        print(info)
