logger = setup_logging()

class CameraManager:
    def __init__(self, cameras: List[Camera]):
        """Initialize camera manager with list of camera objects
        
        Args:
            cameras: List of Camera objects with initialized video captures
        """
        self.logger = logger
        self.cameras = cameras
        self.inference_engine = InferenceEngine()
        self.running = False
        self.camera_threads = {}
        
    def start(self):
        """Start processing all enabled cameras"""
        self.running = True
        for camera in self.cameras:
            if camera.enabled and camera.capture is not None:
                # Start thread for each camera
                thread = threading.Thread(
                    target=self._process_camera,
                    args=(camera,),
                    daemon=True
                )
                thread.start()
                self.camera_threads[camera.camera_id] = thread
                
    def stop(self):
        """Stop all camera processing"""
        self.running = False
        for thread in self.camera_threads.values():
            thread.join()
        self.camera_threads.clear()
                
    def _process_camera(self, camera: Camera):
        """Process video stream from a single camera
        
        Args:
            camera: Camera object to process
        """
        while self.running:
            ret, frame = camera.capture.read()
            if not ret:
                self.logger.error(f"Failed to read frame from camera {camera.camera_id}")
                continue
                
            # Run inference
            detections = self.inference_engine.detect_objects(frame)

            # TODO notify customers based on detection/notification settings
            
            # Draw detection results on frame
            annotated_frame = draw_detections(frame, detections)
            
            # TODO: Publish annotated frame to websocket
            
            # TODO: Store detections in DB via DB client
            # db_client.store_detections(camera.camera_id, detections)

        
    



