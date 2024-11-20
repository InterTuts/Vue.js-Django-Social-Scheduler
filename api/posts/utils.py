class NetworkObj:
    def __init__(self, network_name, net_id, name, token, secret):
        self.network_name=network_name
        self.net_id=net_id
        self.name=name
        self.token=token
        self.secret=secret

class PostObj:
    def __init__(self, text, image):
        self.text=text
        self.image=image