class Location:
    def __init__(self, client_id: str, location_id: str, location_name: str, address: str, timezone: str, fixtures=None):
        self.fixtures = fixtures if fixtures is not None else []
        self.client_id = client_id
        self.location_id = location_id
        self.location_name = location_name
        self.address = address
        self.timezone = timezone

    def __repr__(self):
        return f"Location(client_id={self.client_id}, location_id={self.location_id}, location_name={self.location_name}, address={self.address}, timezone={self.timezone})" 