import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def env(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError("Variável de ambiente não configurada: " + name)
    return value


def supabase_request(method, table, payload=None, query="", prefer=None):
    base = env("SUPABASE_URL").rstrip("/")
    key = env("SUPABASE_SERVICE_ROLE_KEY")
    url = base + "/rest/v1/" + table + (("?" + query) if query else "")
    headers = {
        "apikey": key,
        "Authorization": "Bearer " + key,
        "Accept": "application/json",
    }
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if prefer:
        headers["Prefer"] = prefer
    request = Request(url, data=data, headers=headers, method=method)
    try:
        with urlopen(request, timeout=20) as response:
            raw = response.read().decode("utf-8")
            return json.loads(raw) if raw else []
    except HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")
        raise RuntimeError("Supabase respondeu " + str(error.code) + ": " + detail)
    except URLError as error:
        raise RuntimeError("Não foi possível acessar o Supabase: " + str(error))


def json_response(handler, status, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Access-Control-Allow-Origin", os.environ.get("APP_ORIGIN", "*"))
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def read_json(handler):
    length = int(handler.headers.get("Content-Length", "0"))
    if length > 50000:
        raise ValueError("Corpo da requisição muito grande.")
    return json.loads(handler.rfile.read(length).decode("utf-8") or "{}")
