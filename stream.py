import urllib.parse
import requests
import http.server
from webPlayer.webServer import WebServer

BASE_URL = "https://cms-tvflow.gsports.net.cn/wxtv/"

# Headers
HEADERS = {
    "Host": "cms-tvflow.gsports.net.cn",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 NetType/WIFI "
    "MicroMessenger/7.0.20.1781(0x6700143B) WindowsWechat(0x63090a13) "
    "UnifiedPCWindowsWechat(0xf2540512) XWEB/13871 Flue",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://gsports-wxtv.smgtech.net",
    "Referer": "https://gsports-wxtv.smgtech.net/",
    "Connection": "keep-alive",
}


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        url = self.construct_url(self.path)
        print("代理请求:", url)

        path = urllib.parse.urlparse(url).path

        if path == "":
            WebServer.send_static_html(self)
            return

        # If it is m3u8 file
        if path.endswith(".m3u8"):
            self.handle_m3u8_request(url)
        else:
            self.handle_other_requests(url)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")  # 允许所有域名
        self.send_header(
            "Access-Control-Allow-Methods", "GET, POST, OPTIONS"
        )  # 允许的请求方法
        self.send_header("Access-Control-Allow-Headers", "Content-Type")  # 允许的请求头
        self.end_headers()

    def end_headers(self):
        super().end_headers()

    def construct_url(self, path):
        # Remove the "/" at the beginning first
        path = urllib.parse.unquote(path[1:])

        # A simpler link style like localhost:5623/epg001.m3u8?auth_key=xxxx
        if path.startswith("epg001.m3u8?auth_key="):
            # Complete to standard link
            path = BASE_URL + path

        # For other cases, return the unquoted path
        return path

    def handle_m3u8_request(self, url):
        try:
            resp = requests.get(url, headers=HEADERS)
            resp.raise_for_status()

            lines = resp.text.splitlines()
            new_lines = []

            for line in lines:
                line = line.strip()
                if line == "" or line.startswith("#"):
                    new_lines.append(line)
                else:
                    # Change relative address to absolute url
                    ts_url = urllib.parse.urljoin(BASE_URL, line)
                    # Change it to the proxy address format
                    # to allow third party accessing the local proxy
                    proxy_ts_url = f"http://localhost:{self.server.socket.getsockname()[1]}/{ts_url}"
                    new_lines.append(proxy_ts_url)

            new_m3u8 = "\n".join(new_lines)

            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.apple.mpegurl")
            self.send_header("Content-Length", str(len(new_m3u8.encode("utf-8"))))
            self.send_header("Access-Control-Allow-Origin", "*")  # CORS header
            self.end_headers()
            self.wfile.write(new_m3u8.encode("utf-8"))

        except Exception as e:
            self.send_error(502, f"Bad gateway fetching m3u8: {e}")

    def handle_other_requests(self, url):
        # For non-M3U8 requests, direct proxy forwarding requests with headers
        try:
            resp = requests.get(url, headers=HEADERS, stream=True)
            self.send_response(resp.status_code)

            for k, v in resp.headers.items():
                if k.lower() not in [
                    "content-encoding",
                    "transfer-encoding",
                    "content-length",
                    "connection",
                ]:
                    self.send_header(k, v)

            self.send_header("Content-Length", resp.headers.get("Content-Length", "0"))
            self.end_headers()

            for chunk in resp.iter_content(chunk_size=4096):
                if chunk:
                    self.wfile.write(chunk)

        except Exception as e:
            self.send_error(502, f"Bad gateway: {e}")
