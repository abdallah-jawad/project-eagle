import time
from dependencies.db import DynamoDBClient
from models.client import Client
from models.location import Location
from models.fixture import Fixture
from models.planogram import Planogram
from models.camera import Camera

class PlanogramVision:
    def __init__(self, db_client: DynamoDBClient):
        self.db_client = db_client
        self.clients = self.fetch_clients_enrolled_in_planogram_vision()
        self.locations = {client.client_id: self.db_client.fetch_client_data_for_planogram_vision(client.client_id) for client in self.clients}

    def fetch_clients_enrolled_in_planogram_vision(self):
        # Use the db_client to fetch clients for the PlanogramVision feature
        client_items = self.db_client.fetch_clients_for_feature('PlanogramVision')
        clients = [Client(**item) for item in client_items]
        return clients

    def process_planogram_fixtures(self):
        PROCESS_INTERVAL = 300  # 5 minutes in seconds
        
        while True:
            for client_id, locations in self.locations.items():
                for location in locations:
                    self.run_process_x(location, client_id)

            # Wait for next interval
            time.sleep(PROCESS_INTERVAL)

    def run_process_x(self, location: Location, client_id: str):
        # This method will be implemented later
        # It will process each fixture using the planogram, fixture, location, and camera details
        pass 

    def run_process_y(self, location: Location, client_id: str):
        # This method will be implemented later
        # It will process each fixture using the planogram, fixture, location, and camera details
        pass 