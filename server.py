import config
import socket

# Define a tabela de dados como vazia
table_data = { }

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

# Cria o socket do servidor
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Vincula o servidor ao host e porta
s.bind((config.SERVER_HOST, config.SERVER_PORT))

# Fica em modo escuta, aguardando conexoes de clientes
s.listen(5)

while 1:
    # Aceita conexao e obtem socket e endereco do cliente
    client_socket, address = s.accept()

    # Obtem a requisicao do cliente
    request = client_socket.recv(config.MAX_REQUEST_LENGTH).decode('utf8')

    # Envia a resposta ao cliente (informacao relativa a requisicao)
    if request in table_data:
        client_socket.send(table_data[request].encode('utf8'))
    # Se nao houver nada definido para a requisicao, envia a string "Undefined"
    else:
        client_socket.send(("Undefined").encode('utf8'))
