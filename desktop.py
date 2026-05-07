from threading import Thread

import webview

from app.web import createServer


HOST = "127.0.0.1"
PORT = 5500
APP_URL = f"http://{HOST}:{PORT}"


def startServerInThread():
    server = createServer(HOST, PORT)
    serverThread = Thread(target=server.serve_forever, daemon=True)
    serverThread.start()
    return server, serverThread


def main():
    server, serverThread = startServerInThread()

    try:
        webview.create_window(
            "ServiceManager",
            APP_URL,
            width=1100,
            height=750,
            min_size=(900, 600),
        )
        webview.start()
    finally:
        server.shutdown()
        server.server_close()
        serverThread.join(timeout=2)


if __name__ == "__main__":
    main()
