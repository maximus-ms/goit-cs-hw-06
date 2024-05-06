import pathlib
import logging
import mimetypes
import socket
from datetime import datetime
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from multiprocessing import Process

HTTP_PORT = 3000
SOCKET_PORT = 5000
SERVER_ADDR = socket.gethostbyname(socket.gethostname())
SOCKET_CHUNK_SIZE = 1024

URI_DB = "mongodb://mongodb:27017"


class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message":
            self.send_html_file("message.html")
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers["Content-Length"]))
        data_parse = urllib.parse.unquote_plus(data.decode())
        send_socket(data_parse)
        self.send_response(302)
        self.send_header("Location", "/")
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)[0] or "text/plain"
        self.send_header("Content-type", mt)
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())


def run_http():
    http = HTTPServer((SERVER_ADDR, HTTP_PORT), HttpHandler)
    try:
        logging.info(f"HTTP Server started: http://{SERVER_ADDR}:{HTTP_PORT}")
        http.serve_forever()
    except KeyboardInterrupt as e:
        pass
    except Exception as e:
        logging.error(f"ERR: {e}")
    finally:
        logging.info("HTTP Server stopped")
        http.server_close()


def send_socket(data):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data.encode(), (SERVER_ADDR, SOCKET_PORT))
        sock.close()
    except Exception as e:
        logging.error(e)


def save_to_db(data):
    data_list = [("date", datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))]
    try:
        data_list += [i.split("=") for i in data.split("&")]
        data_dict = dict(data_list)
    except Exception as e:
        logging.error(e)
        return
    logging.info(f"MONGODB to write: {data_dict}")
    try:
        client = MongoClient(URI_DB, server_api=ServerApi("1"))
        db = client.mds02cs_hw_06
        db.messages.insert_one(data_dict)
    except Exception as e:
        logging.error(e)
    finally:
        client.close()


def run_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setblocking(0)
    try:
        sock.bind((SERVER_ADDR, SOCKET_PORT))
        logging.info(
            f"SOCKET Server started: socket://{SERVER_ADDR}:{SOCKET_PORT}"
        )
        while True:
            try:
                data, addr = sock.recvfrom(SOCKET_CHUNK_SIZE)
                logging.info(f"SOCKET received from {addr}: {data.decode()}")
                save_to_db(data.decode())
            except socket.error as e:
                if e.errno != socket.errno.EWOULDBLOCK:
                    logging.error(f"SOCKET: {e}")
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error(f"SOCKET: {e}")
    finally:
        logging.info("SOCKET Server stopped")
        sock.close()


logging.basicConfig(
    level=logging.INFO,
    format="SERVER[%(levelname)s]: [%(asctime)s] %(message)s",
    datefmt="%d/%b/%Y %H:%M:%S",
)


if __name__ == "__main__":
    p_socket = Process(target=run_socket)
    p_socket.start()

    p_http = Process(target=run_http)
    p_http.start()

    try:
        p_http.join()
        p_socket.join()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.error(e)
    finally:
        p_http.terminate()
        p_socket.terminate()
