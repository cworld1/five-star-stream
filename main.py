from stream import ProxyHandler
import socketserver

PORT = 5623


def main():
    server_address = ("", PORT)
    with socketserver.ThreadingTCPServer(server_address, ProxyHandler) as httpd:
        print(f"代理服务器启动，监听端口 {PORT}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
