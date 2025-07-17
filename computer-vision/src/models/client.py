class Client:
    def __init__(self, client_id: str, client_name: str, status: str, contact_info: str):
        self.client_id = client_id
        self.client_name = client_name
        self.status = status
        self.contact_info = contact_info

    def __repr__(self):
        return f"Client(client_id={self.client_id}, client_name={self.client_name}, status={self.status}, contact_info={self.contact_info})" 