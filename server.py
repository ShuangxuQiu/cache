import config
import socket
import time

# Imprime uma mensagem no formato do servidor
def server_print(stepname, message):
    print('[' + time.ctime() + ' - ' + stepname + '] ' + message),

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

print('Feito!')
server_print('Inicializacao', 'Criando socket do servidor... ')

# Cria o socket do servidor
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

print('Feito!')
server_print('Inicializacao', 'Vinculando servidor ao endereco e porta configurados... ')

# Vincula o servidor ao host e porta
s.bind((config.SERVER_HOST, config.SERVER_PORT))

print('Feito!')
server_print('Inicializacao', 'Colocando servidor em modo de escuta... ')

# Fica em modo escuta, aguardando conexoes de clientes
s.listen(5)

print('Feito!')
server_print('Inicializacao', 'Servidor executando em ' + str(config.SERVER_HOST) + ':' + str(config.SERVER_PORT) + '\n')

while 1:
    # Aceita conexao e obtem socket e endereco do cliente
    client_socket, address = s.accept()
    server_print('Conexao', 'Conexao aceita para ' + str(address[0]) + ':' + str(address[1]) + '\n')

    # Obtem a requisicao do cliente
    request = client_socket.recv(config.MAX_REQUEST_LENGTH).decode('utf8')
    server_print('Requisicao', str(address[0]) + ':' + str(address[1]) + ' -> \"' + request + '\", processando e enviando resposta... ')

    # Envia a resposta ao cliente (informacao relativa a requisicao)
    if request in table_data:
        client_socket.send(table_data[request].encode('utf8'))
    # Se nao houver nada definido para a requisicao, envia a string "Undefined"
    else:
        client_socket.send(("Undefined").encode('utf8'))

    print('Feito!')
