import boto3
import time
from typing import List
from models.detection_db_record import DetectionDBRecord
from threading import Thread, Lock
import queue
import json
from datetime import datetime
from models.location import Location
from models.fixture import Fixture
from models.planogram import Planogram
from models.camera import Camera

class DynamoDBClient:
    """Client for interacting with DynamoDB to store detection records"""
    
    def __init__(self, table_name: str = "detections", batch_size: int = 25, flush_interval: int = 30):
        """Initialize DynamoDB client
        
        Args:
            table_name: Name of DynamoDB table to write to
            batch_size: Number of records to batch before writing
            flush_interval: Maximum seconds to wait before flushing queue
        """
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(table_name)
        self.write_queue = queue.Queue()
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.queue_lock = Lock()
        self.last_flush = time.time()
        
        # Start background thread for batch processing
        self.running = True
        self.batch_thread = Thread(target=self._batch_processor, daemon=True)
        self.batch_thread.start()

    def store_detection(self, record: DetectionDBRecord):
        """Queue a detection record for batch writing
        
        Args:
            record: DetectionDBRecord to store in DynamoDB
        """
        # For each detection in the record, create a separate item
        for detection in record.detections:
            # Convert to dict format for DynamoDB
            item = {
                'timestamp': record.timestamp.isoformat(),
                'frame_id': record.frame_id,
                'camera_id': record.camera_id,
                'client_id': record.client_id,
                'zone': record.zone,
                'detection_class': detection.class_name,
                'confidence': detection.confidence,
                'bbox': detection.bbox,
                'class_id': detection.class_id
            }
            
            self.write_queue.put(item)

    def _batch_processor(self):
        """Background thread that processes queued records in batches"""
        while self.running:
            current_batch = []
            
            # Get all available items up to batch size
            while len(current_batch) < self.batch_size:
                try:
                    item = self.write_queue.get_nowait()
                    current_batch.append(item)
                except queue.Empty:
                    break
                    
            # Write batch if we have items and either:
            # 1. We've reached batch size
            # 2. It's been longer than flush_interval since last flush
            if current_batch and (
                len(current_batch) >= self.batch_size or 
                time.time() - self.last_flush > self.flush_interval
            ):
                self._write_batch(current_batch)
                self.last_flush = time.time()
            
            # Small sleep to prevent tight loop
            time.sleep(0.1)

    def _write_batch(self, items: List[dict]):
        """Write a batch of items to DynamoDB
        
        Args:
            items: List of items to write
        """
        try:
            with self.table.batch_writer() as batch:
                for item in items:
                    batch.put_item(Item=item)
        except Exception as e:
            # TODO: Add proper error handling/retry logic
            print(f"Error writing batch to DynamoDB: {e}")

    def shutdown(self):
        """Shutdown the batch processor and flush remaining items"""
        self.running = False
        self.batch_thread.join()
        
        # Flush any remaining items
        remaining_items = []
        while not self.write_queue.empty():
            remaining_items.append(self.write_queue.get())
        if remaining_items:
            self._write_batch(remaining_items)

    def fetch_clients_for_feature(self, feature_name: str):
        # Fetch clients enrolled in a specific feature
        response = self.table.query(
            IndexName='feature_enrollment_index',
            KeyConditionExpression='SK = :feature',
            ExpressionAttributeValues={
                ':feature': f'FEATURE#{feature_name}'
            }
        )
        return response.get('Items', [])

    def fetch_client_data_for_planogram_vision(self, client_id: str):
        # Fetch locations for the client
        locations_response = self.table.query(
            KeyConditionExpression='PK = :client AND begins_with(SK, :location)',
            ExpressionAttributeValues={
                ':client': f'CLIENT#{client_id}',
                ':location': 'LOCATION#'
            }
        )
        locations = locations_response.get('Items', [])

        # Fetch fixtures, planograms, and cameras for each location
        for location in locations:
            fixtures_response = self.table.query(
                KeyConditionExpression='PK = :location AND begins_with(SK, :fixture)',
                ExpressionAttributeValues={
                    ':location': f'LOCATION#{location['location_id']}',
                    ':fixture': 'FIXTURE#'
                }
            )
            location['fixtures'] = fixtures_response.get('Items', [])

            for fixture in location['fixtures']:
                # Fetch planograms
                planograms_response = self.table.query(
                    KeyConditionExpression='PK = :fixture AND begins_with(SK, :planogram)',
                    ExpressionAttributeValues={
                        ':fixture': f'FIXTURE#{fixture['fixture_id']}',
                        ':planogram': 'PLANOGRAM#'
                    }
                )
                fixture['planograms'] = planograms_response.get('Items', [])

                # Fetch cameras
                cameras_response = self.table.query(
                    KeyConditionExpression='PK = :fixture AND begins_with(SK, :camera)',
                    ExpressionAttributeValues={
                        ':fixture': f'FIXTURE#{fixture['fixture_id']}',
                        ':camera': 'CAMERA#'
                    }
                )
                fixture['cameras'] = cameras_response.get('Items', [])

        # Convert raw data to structured models
        structured_locations = []
        for loc in locations:
            location_obj = Location(
                client_id=client_id,
                location_id=loc['location_id'],
                location_name=loc['location_name'],
                address=loc['address'],
                timezone=loc['timezone'],
                fixtures=[
                    Fixture(
                        location_id=loc['location_id'],
                        fixture_id=fix['fixture_id'],
                        fixture_name=fix['fixture_name'],
                        fixture_type=fix['fixture_type'],
                        position=fix['position'],
                        dimensions=fix['dimensions'],
                        planograms=[
                            Planogram(
                                fixture_id=fix['fixture_id'],
                                planogram_id=plan['planogram_id'],
                                planogram_name=plan['planogram_name'],
                                version=plan['version'],
                                layout_data=plan['layout_data'],
                                products=plan['products']
                            ) for plan in fix['planograms']
                        ],
                        cameras=[
                            Camera(
                                fixture_id=fix['fixture_id'],
                                camera_id=cam['camera_id'],
                                camera_name=cam['camera_name'],
                                stream_url=cam['stream_url'],
                                resolution=cam['resolution'],
                                fps=cam['fps'],
                                status=cam['status']
                            ) for cam in fix['cameras']
                        ]
                    ) for fix in loc['fixtures']
                ]
            )
            structured_locations.append(location_obj)

        return structured_locations
