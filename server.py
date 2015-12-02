import config
import socket
import time
import signal
import sys

# Abre o arquivo de log do servidor
log = open(config.SERVER_LOG_FILE, 'a')

# Gerenciador de interrupcoes
def interrupt_handler(signal, frame):
    print('\n')
    server_print('Finalizacao', 'Servidor encerrado com sucesso!')
    sys.exit(0)

# Imprime uma mensagem no formato do servidor
def server_print(stepname, message):
    # Abre o arquivo de log do servidor
    log = open(config.SERVER_LOG_FILE, 'a')

    # Se o tipo do passo for 'Mensagem', imprime apenas a mensagem	
    if stepname == 'Mensagem':
        # Imprime no log
        log.write(message + '\n')
	    # Imprime na tela
        print(message)

    else:
        # Gera a mensagem
        output_msg = '[' + time.ctime() + ' - ' + stepname + '] ' + message
        # Imprime no log
        log.write(output_msg)
	    # Imprime na tela
        print(output_msg),


# Define a tabela de dados como vazia
table_data = { }

server_print('Inicializacao', 'Lendo arquivo de dados... ')

# Abre o arquivo de dados do servidor
with open(config.SERVER_DATAFILE, 'r') as input_file:
    # Le uma linha do arquivo
    for data in input_file:
        # Se existirem comentarios na linha, remove-os
        if data.find('#') != -1:
            data, sep, tail = data.partition('#')

        # Se existir alguma definicao de dados na linha, adiciona-a na tabela
        if data.find('=>') != -1:
            key, sep, value = data.partition('=>')
            table_data[key.strip()] = value.strip()


server_print('Mensagem', 'Feito!')
server_print('Inicializacao', 'Criando socket do servidor... ')

# Cria o socket do servidor
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_print('Mensagem', 'Feito!')
server_print('Inicializacao', 'Vinculando servidor ao endereco e porta configurados... ')

# Vincula o servidor ao host e porta
s.bind((config.SERVER_HOST, config.SERVER_PORT))

server_print('Mensagem', 'Feito!')
server_print('Inicializacao', 'Colocando servidor em modo de escuta... ')

# Fica em modo escuta, aguardando conexoes de clientes
s.listen(5)

server_print('Mensagem', 'Feito!')
server_print('Inicializacao', 'Servidor executando em ' + str(config.SERVER_HOST) + ':' + str(config.SERVER_PORT) + '\n')

# Ativa o gerenciador de interrupcoes
signal.signal(signal.SIGINT, interrupt_handler)

while 1:
    # Aceita conexao e obtem socket e endereco do cliente
    client_socket, address = s.accept()
    server_print('Conexao', 'Conexao aceita para ' + str(address[0]) + ':' + str(address[1]) + '\n')

    # Obtem a requisicao do cliente
    request = client_socket.recv(config.MAX_REQUEST_LENGTH).decode('utf8')
    server_print('Requisicao', str(address[0]) + ':' + str(address[1]) + ' -> \"' + request + '\", processando...\n')

    # Envia a resposta ao cliente (informacao relativa a requisicao)
    if request in table_data:
        # Imprime mensagem avisando o valor a ser enviado
        server_print('Resposta', 'Enviando o valor \'' + table_data[request] + '\' para o cliente... ')
        # Envia resposta ao cliente
        client_socket.send(table_data[request].encode('utf8'))
        # Confirma o envio
        server_print('Mensagem', 'Feito!')

    # Se nao houver nada definido para a requisicao, envia a string
    # definida no arquivo de configuracao
    else:
        client_socket.send(config.MESSAGE_REQUEST_NOT_FOUND.encode('utf8'))
        # Imprime aviso de valor nao encontrado
        server_print('Resposta', 'Valor nao encontrado para a requisicao!\n')


