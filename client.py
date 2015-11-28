import config
import socket

# Cria o socket do cliente
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Realiza a conexao com o servidor
s.connect((config.SERVER_HOST, config.SERVER_PORT))

s.send(b"Info1")

print(s.recv(config.MAX_INFO_LENGTH))
