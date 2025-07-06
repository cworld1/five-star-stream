from stream import ProxyHandler
import socketserver
from webPlayer.webServer import WebServer

PORT = 5623


def main():
    server_address = ("", PORT)
    with socketserver.ThreadingTCPServer(server_address, ProxyHandler) as httpd:
        print(f"代理服务器启动，监听端口 {PORT}")
        WebServer.print_server_link(PORT)
        httpd.serve_forever()


if __name__ == "__main__":
    main()
