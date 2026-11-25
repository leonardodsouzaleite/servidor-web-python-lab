import logging

from WebServerMT import DEFAULT_PORT, accept_connection, prepare_server


def main() -> None:
    logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s [%(threadName)s] %(message)s",)
    server_socket = prepare_server(port=DEFAULT_PORT)
    logging.info("Servidor multithread ouvindo na porta %d", DEFAULT_PORT)

    try:
        accept_connection(server_socket)
    except KeyboardInterrupt:
        logging.info("Encerrando o servidor.")
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
