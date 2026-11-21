import socket

# Define o endereço da porta em que o servidor ficará aguardando requisições HTTP.
serverPort = 6789

# Cria um socket IPv4 (AF_INET) que usa transporte TCP confiável (SOCK_STREAM).
serverSocket = socket(AF_INET, SOCK_STREAM)

# Associa o socket a todas as interfaces locais e à porta definida acima.
serverSocket.bind(('', serverPort))

# Coloca o socket em modo passivo para aceitar conexões de clientes.
serverSocket.listen(1)

# Mantém o servidor executando indefinidamente para atender novos clientes.
while True:
    # Bloqueia até que um cliente estabeleça uma conexão TCP.
    connectionSocket, address = serverSocket.accept()

    try:
        # Recebe uma parte da requisição HTTP enviada pelo cliente.
        message = connectionSocket.recv(1024)

        # Separa os elementos da linha de requisição usando espaços como delimitador.
        parts = message.split()

        # A segunda palavra da requisição HTTP contém o caminho solicitado.
        filename = parts[1]

        # Remove a barra inicial para tratar o nome como caminho relativo ao diretório do projeto.
        filename = filename.decode().lstrip('/')

        try:
            # Abre o arquivo solicitado em modo binário para preservar seu conteúdo.
            file = open(filename, 'rb')

            # Lê todo o conteúdo do arquivo para enviá-lo no corpo da resposta.
            outputdata = file.read()

            # Fecha o arquivo imediatamente após terminar a leitura.
            file.close()

            # Envia o início da resposta HTTP indicando sucesso.
            connectionSocket.send(b'HTTP/1.1 200 OK\r\n')

            # Informa que o conteúdo está no formato HTML para o navegador.
            connectionSocket.send(b'Content-Type: text/html\r\n')

            # Informa o tamanho do corpo para que o cliente saiba onde ele termina.
            connectionSocket.send(b'Content-Length: ' + str(len(outputdata)).encode() + b'\r\n')

            # Separa os cabeçalhos HTTP do corpo com uma linha vazia.
            connectionSocket.send(b'\r\n')

            # Envia os bytes do arquivo solicitado como corpo da resposta.
            connectionSocket.send(outputdata)

        except IOError:
            # Envia o código de status HTTP que indica arquivo não encontrado.
            connectionSocket.send(b'HTTP/1.1 404 Not Found\r\n')

            # Informa o tipo de conteúdo da página de erro simples.
            connectionSocket.send(b'Content-Type: text/html\r\n')

            # Define o texto do corpo da resposta de erro.
            body = b'<html><body><h1>404 Not Found</h1></body></html>'

            # Informa o tamanho da mensagem de erro para o cliente.
            connectionSocket.send(b'Content-Length: ' + str(len(body)).encode() + b'\r\n')

            # Separa os cabeçalhos da mensagem de erro do corpo.
            connectionSocket.send(b'\r\n')

            # Envia o corpo da resposta HTTP com a mensagem de erro.
            connectionSocket.send(body)

    except (IndexError, UnicodeDecodeError):
        # Responde a uma requisição malformada ou incompleta sem derrubar o servidor.
        connectionSocket.send(b'HTTP/1.1 400 Bad Request\r\n\r\n')

    finally:
        # Encerra a conexão TCP após completar a resposta ou detectar um erro.
        connectionSocket.close()
