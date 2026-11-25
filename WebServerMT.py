import logging
import mimetypes
import socket
import threading
from pathlib import Path
from urllib.parse import unquote, urlsplit


DEFAULT_PORT = 6789
DOCUMENT_ROOT = Path(__file__).resolve().parent
LOGGER = logging.getLogger(__name__)



''' Cria e prepara o server para as conexões multithreads '''
def prepare_server(host: str = "", port: int = DEFAULT_PORT, backlog: int = 5) -> socket.socket:

    # cria, configura e retorna o socket que receberá conexões
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:

        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((host, port))
        server_socket.listen(backlog)

    except OSError:

        server_socket.close()
        raise

    return server_socket



''' Busca e lê o arquivo da conexão, também exibe erros caso o arquivo não exista '''
def file_management(request_target: str, document_root: Path | str = DOCUMENT_ROOT) -> tuple[bytes, str]:

    # lê o arquivo sem permitir acesso fora da raiz
    root = Path(document_root).resolve()
    relative_path = unquote(urlsplit(request_target).path).lstrip("/")
    requested_file = (root / relative_path).resolve()

    try:
        requested_file.relative_to(root)

    # tratamento de erros
    except ValueError as error:
        raise FileNotFoundError(request_target) from error

    if not requested_file.is_file():
        raise FileNotFoundError(request_target)

    content = requested_file.read_bytes()
    content_type = mimetypes.guess_type(requested_file.name)[0]

    return content, content_type or "application/octet-stream"



''' Responde em arquivo HTTP com headers '''
def send_response(connection_socket: socket.socket, status: int, reason: str, body: bytes, content_type: str = "text/html; charset=utf-8", extra_headers: tuple[bytes, ...] = ()) -> None:

    # envia a resposta HTTP completa
    headers = [
        f"HTTP/1.1 {status} {reason}".encode("ascii"),
        f"Content-Type: {content_type}".encode("ascii"),
        f"Content-Length: {len(body)}".encode("ascii"),
        b"Connection: close",
        *extra_headers,
    ]
    response = b"\r\n".join(headers) + b"\r\n\r\n" + body
    connection_socket.sendall(response)



''' Faz o atendimento, recebendo e interpretando a requisição '''
def handle_client(connection_socket: socket.socket, address: tuple[str, int]):
    
    # interpreta uma requisição, envia a resposta e fecha a conexão
    try:
        request = connection_socket.recv(4096)
        request_line = request.split(b"\r\n", 1)[0].split()

        # tratamentos de muitos erros possíveis
        if len(request_line) != 3:
            send_response(connection_socket, 400, "Bad Request", b"<html><body><h1>400 Bad Request</h1></body></html>",)
            return

        method, raw_target, version = request_line
        if version not in (b"HTTP/1.0", b"HTTP/1.1"):
            send_response(connection_socket, 400, "Bad Request", b"<html><body><h1>400 Bad Request</h1></body></html>",)
            return

        if method != b"GET":
            send_response(connection_socket, 405, "Method Not Allowed", b"<html><body><h1>405 Method Not Allowed</h1></body></html>", extra_headers=(b"Allow: GET",),)
            return

        try:
            request_target = raw_target.decode("ascii")
            body, content_type = file_management(request_target)

        # tratamentos de muitos erros possíveis 2
        except (UnicodeDecodeError, ValueError):
            send_response(connection_socket, 400, "Bad Request", b"<html><body><h1>400 Bad Request</h1></body></html>",)
            return
        
        except FileNotFoundError:
            send_response(connection_socket, 404, "Not Found",b"<html><body><h1>404 Not Found</h1></body></html>",)
            return
        
        except PermissionError:
            send_response(connection_socket, 403, "Forbidden",b"<html><body><h1>403 Forbidden</h1></body></html>",)
            return
        
        except OSError:
            LOGGER.exception("Erro ao ler o arquivo solicitado por %s", address)
            send_response(connection_socket, 500, "Internal Server Error", b"<html><body><h1>500 Internal Server Error</h1></body></html>",)
            return

        send_response(connection_socket, 200, "OK", body, content_type)
        LOGGER.info("Requisição GET atendida para %s", address)

    except OSError:
        LOGGER.exception("Erro de comunicação com o cliente %s", address)

    finally:
        connection_socket.close()



''' Diferentemente do WebServer.py, não espera a resposta ser concluída para receber outra conexão e criar uma thread nova '''
def accept_connection(server_socket: socket.socket):

    # aceita conexões múltiplas e inicia uma thread para cada cliente
    while True:

        connection_socket, address = server_socket.accept()
        LOGGER.info("Conexão recebida de %s", address)
        client_thread = threading.Thread(target=handle_client, args=(connection_socket, address), name=f"cliente-{address[0]}:{address[1]}", daemon=True,)
        client_thread.start()
