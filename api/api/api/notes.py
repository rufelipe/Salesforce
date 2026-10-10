from api._data import APIHandler, notes


class handler(APIHandler):
    def do_GET(self):
        self.send_json(200, notes())
