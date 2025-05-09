#!/usr/bin/env python3
"""
Video processing module for handling video files and streams.
"""

import time
import cv2
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from service.inference import InferenceEngine
from service.image import draw_detections
from utils import setup_logging

logger = setup_logging()

class VideoProcessor:
    def __init__(self, inference_engine: InferenceEngine):
        """
        Initialize the VideoProcessor with an inference engine.
        
        Args:
            inference_engine: The inference engine to use for object detection
        """
        self.logger = logger
        self.inference_engine = inference_engine
        self._inference_times = []  # Store inference times for statistics
        self._last_frame_time = 0  # For FPS calculation

    def _setup_video_capture(self, source: str) -> Tuple[bool, str, Optional[cv2.VideoCapture], Optional[Dict[str, Any]]]:
        """
        Set up video capture and get video properties.
        
        Args:
            source: Path or URL to the video source
            
        Returns:
            Tuple of (success: bool, message: str, capture: Optional[VideoCapture], properties: Optional[Dict])
        """
        try:
            cap = cv2.VideoCapture(source)
            if not cap.isOpened():
                return False, f"Failed to open video source: {source}", None, None
                
            # Get video properties
            properties = {
                'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            }
            
            self.logger.info(
                f"Video properties: {properties['width']}x{properties['height']} "
                f"@ {properties['fps']} FPS, {properties['total_frames']} frames"
            )
            
            return True, "Video capture setup successful", cap, properties
                
        except Exception as e:
            return False, f"Error setting up video capture: {str(e)}", None, None

    def _setup_video_writer(self, output_path: str, properties: Dict[str, Any]) -> Tuple[bool, str, Optional[cv2.VideoWriter]]:
        """
        Set up video writer for saving processed frames.
        
        Args:
            output_path: Path to save the output video
            properties: Dictionary containing video properties
            
        Returns:
            Tuple of (success: bool, message: str, writer: Optional[VideoWriter])
        """
        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(
                output_path,
                fourcc,
                properties['fps'],
                (properties['width'], properties['height'])
            )
            self.logger.info(f"Will save output to: {output_path}")
            return True, "Video writer setup successful", writer
                
        except Exception as e:
            return False, f"Error setting up video writer: {str(e)}", None

    def _process_frame(self, frame: cv2.Mat) -> Tuple[cv2.Mat, float]:
        """
        Process a single frame through the inference engine.
        
        Args:
            frame: Input frame to process
            
        Returns:
            Tuple of (processed frame with detections drawn, inference time in milliseconds)
        """
        # Time the inference
        inference_start = time.time()
        results = self.inference_engine.run_inference(frame)
        inference_time = (time.time() - inference_start) * 1000  # Convert to milliseconds
        
        # Store inference time for statistics
        self._inference_times.append(inference_time)
        
        # Calculate actual FPS based on time between frames
        current_time = time.time()
        if self._last_frame_time > 0:
            frame_time = current_time - self._last_frame_time
            actual_fps = 1.0 / frame_time if frame_time > 0 else 0
            self.logger.debug(f"Frame time: {frame_time*1000:.1f}ms, Actual FPS: {actual_fps:.1f}")
        self._last_frame_time = current_time
        
        return draw_detections(frame, results), inference_time

    def _get_timing_statistics(self) -> Dict[str, float]:
        """
        Calculate timing statistics from collected inference times.
        
        Returns:
            Dictionary containing timing statistics
        """
        if not self._inference_times:
            return {
                'min': 0.0,
                'max': 0.0,
                'avg': 0.0,
                'total_frames': 0
            }
            
        return {
            'min': min(self._inference_times),
            'max': max(self._inference_times),
            'avg': sum(self._inference_times) / len(self._inference_times),
            'total_frames': len(self._inference_times)
        }

    def _log_progress(self, total_processed: int, total_frames: int, start_time: float, 
                     window_processed: int = 0, window_start_time: float = 0) -> None:
        """
        Log processing progress and performance metrics.
        
        Args:
            total_processed: Total number of frames processed
            total_frames: Total number of frames in video
            start_time: Start time of processing
            window_processed: Number of frames processed in current window
            window_start_time: Start time of current window
        """
        elapsed = time.time() - start_time
        overall_fps = total_processed / elapsed if elapsed > 0 else 0
        
        # Get timing statistics
        stats = self._get_timing_statistics()
        
        if total_frames > 0:  # For video files
            progress = (total_processed / total_frames) * 100
            self.logger.info(
                f"Progress: {progress:.1f}% - "
                f"Processed {total_processed}/{total_frames} frames - "
                f"FPS: {overall_fps:.1f} - "
                f"Inference: {stats['avg']:.1f}ms (min: {stats['min']:.1f}ms, max: {stats['max']:.1f}ms)"
            )
        else:  # For live streams
            if window_processed > 0:
                window_elapsed = time.time() - window_start_time
                window_fps = window_processed / window_elapsed if window_elapsed > 0 else 0
                self.logger.info(
                    f"Live processing - "
                    f"Window FPS: {window_fps:.1f} - "
                    f"Overall FPS: {overall_fps:.1f} - "
                    f"Inference: {stats['avg']:.1f}ms (min: {stats['min']:.1f}ms, max: {stats['max']:.1f}ms)"
                )

    def _cleanup(self, cap: Optional[cv2.VideoCapture], writer: Optional[cv2.VideoWriter]) -> None:
        """
        Clean up video capture and writer resources.
        
        Args:
            cap: Video capture object to release
            writer: Video writer object to release
        """
        if cap is not None:
            cap.release()
        if writer is not None:
            writer.release()
        cv2.destroyAllWindows()
        
        # Log final timing statistics
        stats = self._get_timing_statistics()
        self.logger.info(
            f"Final timing statistics for {stats['total_frames']} frames:\n"
            f"  Average inference time: {stats['avg']:.1f}ms\n"
            f"  Minimum inference time: {stats['min']:.1f}ms\n"
            f"  Maximum inference time: {stats['max']:.1f}ms"
        )
        
        # Reset timing statistics
        self._inference_times = []
        self._last_frame_time = 0

    def process_video_file(self, video_path: str, output_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Process a video file and save the results.
        
        Args:
            video_path: Path to the input video file
            output_path: Optional path to save the processed video
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Setup video capture
            success, message, cap, properties = self._setup_video_capture(video_path)
            if not success:
                return False, message
                
            # Setup video writer if output is requested
            writer = None
            if output_path:
                success, message, writer = self._setup_video_writer(output_path, properties)
                if not success:
                    self._cleanup(cap, None)
                    return False, message
            
            # Process frames
            total_processed_frames = 0
            start_time = time.time()
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process frame
                vis_frame, inference_time = self._process_frame(frame)
                
                # Write frame to output video if requested
                if writer:
                    writer.write(vis_frame)
                
                total_processed_frames += 1
                
                # Log progress every 100 frames
                if total_processed_frames % 100 == 0:
                    self._log_progress(total_processed_frames, properties['total_frames'], start_time)
            
            # Log final statistics
            self._log_progress(total_processed_frames, properties['total_frames'], start_time)
            
            # Cleanup
            self._cleanup(cap, writer)
            
            return True, "Video processing completed successfully"
                
        except Exception as e:
            self.logger.error(f"Error during video processing: {str(e)}")
            return False, str(e)

    def process_video_file_live(self, video_path: str) -> Tuple[bool, str]:
        """
        Process a video file and display results in real-time.
        
        Args:
            video_path: Path to the input video file
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Setup video capture
            success, message, cap, properties = self._setup_video_capture(video_path)
            if not success:
                return False, message
            
            # Process frames
            total_processed_frames = 0
            start_time = time.time()
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process frame
                vis_frame, inference_time = self._process_frame(frame)
                
                # Display frame
                cv2.imshow("Video Detection", vis_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                total_processed_frames += 1
                
                # Log progress every 100 frames
                if total_processed_frames % 100 == 0:
                    self._log_progress(total_processed_frames, properties['total_frames'], start_time)
            
            # Log final statistics
            self._log_progress(total_processed_frames, properties['total_frames'], start_time)
            
            # Cleanup
            self._cleanup(cap, None)
            
            return True, "Video processing completed successfully"
                
        except Exception as e:
            self.logger.error(f"Error during video processing: {str(e)}")
            return False, str(e)

    def process_live_stream(self, stream_url: str) -> Tuple[bool, str]:
        """
        Process a live video stream and display results in real-time.
        
        Args:
            stream_url: URL or path to the video stream
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Setup video capture
            success, message, cap, properties = self._setup_video_capture(stream_url)
            if not success:
                return False, message
            
            self.logger.info(f"Processing live stream from: {stream_url}")
            
            # Process frames
            total_processed_frames = 0
            window_processed_frames = 0
            start_time = time.time()
            window_start_time = start_time
            log_interval = 1.0  # Log every 1 second
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process frame
                vis_frame, inference_time = self._process_frame(frame)
                
                # Display frame
                cv2.imshow("Live Stream Detection", vis_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
                total_processed_frames += 1
                window_processed_frames += 1
                
                # Log performance metrics every second
                current_time = time.time()
                if current_time - window_start_time >= log_interval:
                    self._log_progress(
                        total_processed_frames, 0, start_time,
                        window_processed_frames, window_start_time
                    )
                    window_processed_frames = 0
                    window_start_time = current_time
            
            # Cleanup
            self._cleanup(cap, None)
            
            return True, "Stream processing completed successfully"
                
        except Exception as e:
            self.logger.error(f"Error during stream processing: {str(e)}")
            return False, str(e)
