from main import app
from wsgiref.simple_server import make_server

if __name__ == "__main__":
    server = make_server("0.0.0.0", 8000, app)
    print("Serving on http://0.0.0.0:8000")
    server.serve_forever()