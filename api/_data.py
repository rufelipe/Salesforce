import json
from http.server import BaseHTTPRequestHandler

from main import SalesforceDemoAdapter


adapter = SalesforceDemoAdapter()


def tasks():
    result = []
    for index, item in enumerate(adapter.buscar_tarefas(), start=1045):
        result.append({
            "id": str(index),
            "url": "/?task=" + str(index),
            "title": item.get("titulo", ""),
            "owner": item.get("responsavel", ""),
            "due": item.get("prazo", ""),
            "status": item.get("status", ""),
            "stage": item.get("etapa", ""),
            "contract": item.get("contrato", ""),
            "response": item.get("resposta", ""),
            "observation": item.get("observacao", ""),
            "priority": item.get("prioridade", ""),
            "related": item.get("relacionado", ""),
        })
    return result


def notes():
    import re
    result = []
    for item in adapter.buscar_anotacoes():
        contact = item.get("contato", "")
        match = re.search(r"(\\d+)", str(contact))
        contract = match.group(1) if match else ""
        result.append({
            "contact": contact, "text": item.get("texto", ""),
            "contract": contract, "url": "/?contract=" + contract if contract else ""
        })
    return result


class APIHandler(BaseHTTPRequestHandler):
    def send_json(self, status, payload):
        content = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length > 100000:
            raise ValueError("Corpo da requisição muito grande.")
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw or "{}")

    def log_message(self, format, *args):
        return
