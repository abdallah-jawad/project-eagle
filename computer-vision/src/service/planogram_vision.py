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
        self.client_data = {client.client_id: self.db_client.fetch_client_data(client.client_id) for client in self.clients}

    def fetch_clients_enrolled_in_planogram_vision(self):
        # Use the db_client to fetch clients for the PlanogramVision feature
        client_items = self.db_client.fetch_clients_for_feature('PlanogramVision')
        clients = [Client(**item) for item in client_items]
        return clients

    def fetch_client_data(self, client_id: str):
        # Fetch locations for the client
        locations_response = self.db_client.table.query(
            KeyConditionExpression='PK = :client AND begins_with(SK, :location)',
            ExpressionAttributeValues={
                ':client': f'CLIENT#{client_id}',
                ':location': 'LOCATION#'
            }
        )
        locations = [Location(**item) for item in locations_response.get('Items', [])]

        # Fetch fixtures, planograms, and cameras for each location
        for location in locations:
            fixtures_response = self.db_client.table.query(
                KeyConditionExpression='PK = :location AND begins_with(SK, :fixture)',
                ExpressionAttributeValues={
                    ':location': f'LOCATION#{location.location_id}',
                    ':fixture': 'FIXTURE#'
                }
            )
            fixtures = [Fixture(**item) for item in fixtures_response.get('Items', [])]

            for fixture in fixtures:
                # Fetch planograms
                planograms_response = self.db_client.table.query(
                    KeyConditionExpression='PK = :fixture AND begins_with(SK, :planogram)',
                    ExpressionAttributeValues={
                        ':fixture': f'FIXTURE#{fixture.fixture_id}',
                        ':planogram': 'PLANOGRAM#'
                    }
                )
                fixture.planograms = [Planogram(**item) for item in planograms_response.get('Items', [])]

                # Fetch cameras
                cameras_response = self.db_client.table.query(
                    KeyConditionExpression='PK = :fixture AND begins_with(SK, :camera)',
                    ExpressionAttributeValues={
                        ':fixture': f'FIXTURE#{fixture.fixture_id}',
                        ':camera': 'CAMERA#'
                    }
                )
                fixture.cameras = [Camera(**item) for item in cameras_response.get('Items', [])]

        return locations

    def process_fixtures(self):
        for client_id, locations in self.client_data.items():
            for location in locations:
                for fixture in location.fixtures:
                    # Placeholder for process X
                    self.run_process_x(fixture, location)

    def run_process_x(self, fixture: Fixture, location: Location):
        # This method will be implemented later
        # It will process each fixture using the planogram, fixture, location, and camera details
        pass