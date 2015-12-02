import config
import socket
import time
import datetime


# Tabela cache
cache_table = { }
# Ponteiro da tabela cache
cache_ptr = 0

# Abre o arquivo de log do servidor
log = open(config.CLIENT_LOG_FILE, 'a')


# Imprime uma mensagem no formato do cliente
def client_print(stepname, message):
    # Abre o arquivo de log do servidor
    log = open(config.CLIENT_LOG_FILE, 'a')

    # Se o tipo do passo for 'Resposta', imprime apenas a mensagem    
    if stepname == 'Mensagem':
        log.write(message)
    else:
        log.write('[' + time.ctime() + ' - ' + stepname + '] ' + message)


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
    # Abre o arquivo de log do servidor
    log = open(config.CLIENT_LOG_FILE, 'a')

    # Imprime no log
    client_print('Comando', 'Executei o comando \'/cache\' para imprimir a cache:\n\n')

    # Imprime cabecalho
    log.write('    REQUEST - INFO - TIMESTAMP\n')
    print('REQUEST - INFO - TIMESTAMP')


    # Percorre todas as entradas da tabela
    for i in cache_table:
        # Se a entrada atual nao expirou sua validade
        if cache_table[i]['timestamp'] > time.time() - config.CACHE_EXPIRATION_TIME:
            # Imprime suas informacoes
            output_msg = cache_table[i]['key'] + ' - ' + cache_table[i]['value'] + ' - ' + datetime.datetime.fromtimestamp(cache_table[i]['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            log.write('    ' + output_msg + '\n')
            print(output_msg)

    # Pular linha no log
    log.write('\n')

client_print('Inicializacao', 'Execucao do cliente iniciada!\n\n')

# Loop principal do programa
while 1:
    try:
        # Le entrada do usuario
        input_buffer = raw_input('> ').strip().encode('utf-8')
    except UnicodeDecodeError:
        input_buffer = ''
        print('Caracteres especiais nao sao validos para a entrada!')

    # Verifica se o tamanho da entrada e maior que zero
    if len(input_buffer) > 0:
        # Se comeca com o caractere '/', entao trata como um comando
        if input_buffer[0] == '/':
             # Comando para imprimir a tabela cache
             if input_buffer[1:] == 'cache':
                 print_cache()

             # Comando para sair do programa
             elif input_buffer[1:] == 'exit':
                 client_print('Comando', 'Executei o comando \'/exit\' para encerrar o cliente:\n\n')
                 client_print('Finalizacao', 'Cliente finalizado!\n')
                 exit(0)

             # Se o comando nao e conhecido, imprime um erro na tela
             else:
                 client_print('Comando', 'Comando \'/' + input_buffer[1:] + '\' desconhecido!\n')
                 print('Unknown command: ' + input_buffer[1:])

        # Caso contrario, e uma entrada
        else:
            # Verifica se a entrada esta na tabela cache 
            info = get_cache_value(input_buffer)

            # Se nao estiver, conecta ao servidor para obter sua informacao
            if info is None:
                # Imprime mensagem caso o cliente precise fazer requisicao ao servidor
                client_print('Aviso', 'Nao encontrei \'' + input_buffer + '\' na cache\n')
                client_print('Requisicao', 'Fiz uma requisicao de \'' + input_buffer + '\' para o servidor\n')

                # Cria o socket do cliente
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                # Realiza a conexao com o servidor
                s.connect((config.SERVER_HOST, config.SERVER_PORT))

                # Envia requisicao
                s.send(input_buffer)

                # Aguarda resposta do servidor
                info = s.recv(config.MAX_INFO_LENGTH).decode('utf8')

                # Salva na cache
                insert_cache_value(input_buffer, info)

                # Imprime informacao no log
                client_print('Resposta', 'Recebi \'' + info + '\' como resposta\n\n')

                # Imprime informacao para o usuario
                print(info)

            else:

                # Imprime mensagem caso o cliente encontre o valor na cache
                client_print('Aviso', 'Encontrei \'' + input_buffer + '\' na cache\n')

                # Imprime informacao no log
                client_print('Resposta', info + '\n\n')

                # Imprime informacao para o usuario
                print(info)
