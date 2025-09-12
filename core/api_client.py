"""
WaveSpeed AI API Client Module

This module handles all API interactions with the WaveSpeed AI services.
"""

import requests
import json
import time
import base64
import io
from PIL import Image
from typing import Optional, Tuple, Callable, Dict, Any, Union
from pathlib import Path

from app.config import Config
from app.constants import (
    ApiKey, RequestId, ImagePath, Prompt, Balance, Duration, Seed, 
    GuidanceScale, Creativity, Resolution, OutputFormat, HTTPStatusCodes
)
from core.logger import get_logger
from core.exceptions import (
    APIError, AuthenticationError, RateLimitError, InsufficientBalanceError,
    ValidationError, FileError, ImageProcessingError, NetworkError, 
    TimeoutError, TaskError, TaskFailedError, TaskTimeoutError,
    handle_api_error, handle_validation_error, handle_file_error,
    handle_network_error, handle_timeout_error
)
from core.validation import (
    validate_api_key, validate_image_file, validate_prompt, validate_seed,
    validate_guidance_scale, validate_creativity, validate_duration,
    validate_resolution, validate_output_format, validate_http_status_code
)

logger = get_logger()


class WaveSpeedAPIClient:
    """Client for interacting with WaveSpeed AI APIs"""
    
    def __init__(self) -> None:
        # Validate API key on initialization
        is_valid, error = validate_api_key(Config.API_KEY)
        if not is_valid:
            raise AuthenticationError(f"Invalid API key: {error}")
        
        self.api_key: ApiKey = Config.API_KEY
        self.base_url: str = Config.BASE_URL
        self.session: requests.Session = requests.Session()  # Reuse connections
        self.session.headers.update({
            'User-Agent': 'WaveSpeedAI-GUI/2.0'
        })
        
    def get_headers(self, content_type: str = "application/json") -> Dict[str, str]:
        """Get standard headers for API requests"""
        return {
            "Content-Type": content_type,
            "Authorization": f"Bearer {self.api_key}",
        }
    
    def convert_image_to_base64(self, image_path: Union[str, Path]) -> Optional[str]:
        """Convert image file to base64 string"""
        try:
            # Validate image file first
            is_valid, error = validate_image_file(image_path)
            if not is_valid:
                raise ImageProcessingError(f"Invalid image file: {error}", str(image_path))
            
            with Image.open(image_path) as img:
                # Apply EXIF orientation correction
                from PIL import ImageOps
                img = ImageOps.exif_transpose(img)
                
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                
                image_base64 = base64.b64encode(buffer.getvalue()).decode()
                return image_base64
                
        except ImageProcessingError:
            raise
        except Exception as e:
            raise ImageProcessingError(f"Error converting image to base64: {str(e)}", str(image_path))
    
    def get_balance(self) -> Tuple[Optional[Balance], Optional[str]]:
        """Get account balance from WaveSpeed AI API"""
        try:
            url = Config.ENDPOINTS['balance']
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            logger.info(f"Fetching account balance from: {url}")
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == HTTPStatusCodes.OK:
                result = response.json()
                if result.get('code') == 200 and 'data' in result:
                    balance = result['data'].get('balance', 0.0)
                    logger.info(f"Account balance retrieved: ${balance}")
                    return balance, None
                else:
                    error_msg = result.get('message', 'Unknown error')
                    logger.error(f"Balance API error: {error_msg}")
                    return None, error_msg
            else:
                # Use enhanced error handling
                is_valid, error_msg = validate_http_status_code(response.status_code)
                if not is_valid:
                    logger.error(f"Balance API request failed: {error_msg}")
                    return None, error_msg
                
        except requests.exceptions.Timeout:
            raise handle_timeout_error(10.0, "Balance request timed out")
        except requests.exceptions.RequestException as e:
            raise handle_network_error(url, f"Balance request failed: {str(e)}")
        except Exception as e:
            raise APIError(f"Unexpected error getting balance: {str(e)}")
    
    def submit_image_edit_task(self, image_path: Union[str, Path], prompt: str, output_format: str = "png") -> Tuple[Optional[RequestId], Optional[str]]:
        """Submit image editing task to WaveSpeed AI"""
        try:
            # Validate inputs
            is_valid, error = validate_prompt(prompt)
            if not is_valid:
                raise handle_validation_error("prompt", prompt, error)
            
            is_valid, error = validate_output_format(output_format, "image")
            if not is_valid:
                raise handle_validation_error("output_format", output_format, error)
            
            logger.info(f"Submitting image edit task for: {image_path}")
            
            # Convert image to base64
            image_base64 = self.convert_image_to_base64(image_path)
            if not image_base64:
                raise ImageProcessingError("Failed to convert image to base64", str(image_path))
            
            url = Config.ENDPOINTS['image_edit']
            headers = self.get_headers()
            payload = {
                "enable_base64_output": False,
                "enable_sync_mode": False,
                "images": [f"data:image/png;base64,{image_base64}"],
                "output_format": output_format,
                "prompt": prompt
            }
            
            response = self.session.post(url, headers=headers, 
                                       data=json.dumps(payload), 
                                       timeout=Config.TIMEOUT)
            
            if response.status_code == HTTPStatusCodes.OK:
                result = response.json()["data"]
                request_id = result["id"]
                logger.log_api_request("image_edit", request_id, "submitted")
                return request_id, None
            else:
                raise handle_api_error(response, url)
                
        except (ValidationError, ImageProcessingError, APIError):
            raise
        except Exception as e:
            raise APIError(f"Error submitting image edit task: {str(e)}")
    
    def submit_seededit_task(self, image_url, prompt, guidance_scale=0.5, seed=-1):
        """Submit SeedEdit image editing task to WaveSpeed AI"""
        try:
            logger.info(f"Submitting SeedEdit task with prompt: {prompt[:50]}...")
            
            url = Config.ENDPOINTS['seededit']
            headers = self.get_headers()
            payload = {
                "enable_base64_output": False,
                "guidance_scale": guidance_scale,
                "image": image_url,
                "prompt": prompt,
                "seed": seed
            }
            
            response = self.session.post(url, headers=headers, 
                                       data=json.dumps(payload), 
                                       timeout=Config.TIMEOUT)
            
            if response.status_code == 200:
                result = response.json()["data"]
                request_id = result["id"]
                logger.log_api_request("seededit", request_id, "submitted")
                return request_id, None
            else:
                error_msg = f"API Error: {response.status_code}, {response.text}"
                logger.error(error_msg)
                return None, error_msg
                
        except Exception as e:
            error_msg = f"Error submitting SeedEdit task: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    def submit_seedream_v4_task(self, prompt, images, size="2048*2048", seed=-1, 
                                enable_sync_mode=False, enable_base64_output=False):
        """
        Submit a task to ByteDance Seedream V4 API
        
        Args:
            prompt (str): The editing instruction
            images (list): List of image URLs for multi-modal input
            size (str): Output size in format "width*height" (e.g., "2048*2048")
            seed (int): Random seed for reproducible results (-1 for random)
            enable_sync_mode (bool): Enable synchronous processing
            enable_base64_output (bool): Enable base64 output format
        
        Returns:
            dict: API response with success status and result data
        """
        try:
            import time
            start_time = time.time()
            
            # Validate inputs
            if not prompt or not prompt.strip():
                return {
                    'success': False,
                    'error': 'Prompt is required'
                }
            
            if not images or not isinstance(images, list):
                return {
                    'success': False,
                    'error': 'At least one input image is required'
                }
            
            # Validate size format
            if not self._validate_seedream_v4_size(size):
                return {
                    'success': False,
                    'error': f'Invalid size format: {size}. Expected format: "width*height"'
                }
            
            # Validate seed range
            if seed != -1 and (seed < 0 or seed > 2147483647):
                return {
                    'success': False,
                    'error': 'Seed must be -1 (random) or between 0 and 2147483647'
                }
            
            # Prepare request data
            data = {
                "prompt": prompt.strip(),
                "images": images,  # Array of image URLs
                "size": size,
                "seed": seed,
                "enable_sync_mode": enable_sync_mode,
                "enable_base64_output": enable_base64_output
            }
            
            logger.info(f"Submitting Seedream V4 task with {len(images)} images, size: {size}, seed: {seed}")
            
            # Submit request
            response = self.session.post(
                Config.ENDPOINTS['seedream_v4'],
                json=data,
                headers=self.get_headers(),
                timeout=300  # 5 minute timeout for large images
            )
            
            # Handle response
            if response.status_code == 200:
                result = response.json()
                
                # Check API response format (code, message, data)
                if result.get('code') == 200:
                    data = result.get('data', {})
                    task_id = data.get('id')
                    
                    if task_id:
                        duration = time.time() - start_time
                        
                        # Log successful API request
                        logger.info("=" * 60)
                        logger.info("SEEDREAM V4 API SUCCESS")
                        logger.info("=" * 60)
                        logger.info(f"Task ID: {task_id}")
                        logger.info(f"Duration: {duration:.2f}s")
                        logger.info(f"Prompt: {prompt}")
                        logger.info(f"Size: {size}")
                        logger.info(f"Seed: {seed}")
                        images_info = f"Images Count: {len(images) if images else 0}"
                        if images:
                            images_info += f" (first image size: {len(images[0])} bytes)"
                        logger.info(images_info)
                        logger.info(f"Sync Mode: {enable_sync_mode}")
                        logger.info(f"Base64 Output: {enable_base64_output}")
                        logger.info("=" * 60)
                        
                        return {
                            'success': True,
                            'task_id': task_id,
                            'duration': duration,
                            'metadata': {
                                'prompt': prompt,
                                'size': size,
                                'seed': seed,
                                'input_images_count': len(images),
                                'sync_mode': enable_sync_mode,
                                'base64_output': enable_base64_output
                            }
                        }
                    else:
                        return {
                            'success': False,
                            'error': 'No task ID in response'
                        }
                else:
                    error_msg = result.get('message', 'Unknown API error')
                    
                    # Log detailed API error information
                    logger.error("=" * 60)
                    logger.error("SEEDREAM V4 API ERROR")
                    logger.error("=" * 60)
                    logger.error(f"Error Code: {result.get('code')}")
                    logger.error(f"Error Message: {error_msg}")
                    logger.error(f"Full Response: {result}")
                    logger.error(f"Request Data: {data}")
                    logger.error("=" * 60)
                    
                    return {
                        'success': False,
                        'error': error_msg
                    }
            
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"Seedream V4 request failed: {error_msg}")
                
                # Log detailed API error information
                logger.error("=" * 60)
                logger.error("SEEDREAM V4 API ERROR DETAILS")
                logger.error("=" * 60)
                logger.error(f"Status Code: {response.status_code}")
                logger.error(f"Response Text: {response.text}")
                logger.error(f"Request URL: {Config.ENDPOINTS['seedream_v4']}")
                logger.error(f"Request Data: {data}")
                logger.error("=" * 60)
                
                # Try to parse error details
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg = error_data['error']
                        logger.error(f"Parsed Error: {error_msg}")
                except:
                    pass
                
                return {
                    'success': False,
                    'error': f"API request failed: {error_msg}"
                }
        
        except Exception as e:
            logger.error(f"Seedream V4 submission error: {e}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def get_seedream_v4_result(self, task_id):
        """
        Get the result of a Seedream V4 task
        
        Args:
            task_id (str): The task ID returned from submit_seedream_v4_task
        
        Returns:
            dict: API response with success status and result data
        """
        try:
            # Get result URL
            result_url = f"https://api.wavespeed.ai/api/v3/predictions/{task_id}/result"
            
            logger.info(f"Getting Seedream V4 result for task: {task_id}")
            
            # Get result
            response = self.session.get(
                result_url,
                headers=self.get_headers(),
                timeout=30
            )
            
            # Handle response
            if response.status_code == 200:
                result = response.json()
                
                # Check API response format (code, message, data)
                if result.get('code') == 200:
                    data = result.get('data', {})
                    status = data.get('status')
                    
                    if status == 'completed':
                        outputs = data.get('outputs', [])
                        if outputs:
                            output_url = outputs[0]  # First output URL
                            logger.info(f"Seedream V4 task completed. Output URL: {output_url}")
                            
                            return {
                                'success': True,
                                'status': 'completed',
                                'output_url': output_url,
                                'task_id': task_id,
                                'metadata': {
                                    'inference_time': data.get('timings', {}).get('inference'),
                                    'created_at': data.get('created_at'),
                                    'has_nsfw': data.get('has_nsfw_contents', [False])[0] if data.get('has_nsfw_contents') else False
                                }
                            }
                        else:
                            return {
                                'success': False,
                                'error': 'No outputs in completed result'
                            }
                    elif status == 'failed':
                        error_msg = data.get('error', 'Task failed')
                        logger.error(f"Seedream V4 task failed: {error_msg}")
                        return {
                            'success': False,
                            'status': 'failed',
                            'error': error_msg
                        }
                    else:
                        # Still processing
                        return {
                            'success': True,
                            'status': status,
                            'task_id': task_id
                        }
                else:
                    error_msg = result.get('message', 'Unknown API error')
                    logger.error(f"Seedream V4 result API error: {error_msg}")
                    return {
                        'success': False,
                        'error': error_msg
                    }
            
            else:
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"Seedream V4 result request failed: {error_msg}")
                
                return {
                    'success': False,
                    'error': error_msg
                }
                
        except Exception as e:
            logger.error(f"Error getting Seedream V4 result: {e}")
            return {
                'success': False,
                'error': f"Error getting result: {str(e)}"
            }
    
    def _validate_seedream_v4_size(self, size):
        """Validate Seedream V4 size format"""
        try:
            if not isinstance(size, str) or '*' not in size:
                return False
            
            width_str, height_str = size.split('*')
            width = int(width_str)
            height = int(height_str)
            
            # Check if dimensions are within supported range (256-4096)
            min_size = 256
            max_size = 4096
            
            return (min_size <= width <= max_size and 
                    min_size <= height <= max_size)
            
        except (ValueError, AttributeError):
            return False
    
    def submit_image_upscale_task(self, image_url, target_resolution="4k", creativity=0, output_format="png"):
        """Submit image upscaling task to WaveSpeed AI"""
        try:
            url = f"{self.base_url}/wavespeed-ai/image-upscaler"
            headers = self.get_headers()
            payload = {
                "creativity": creativity,
                "enable_base64_output": False,
                "enable_sync_mode": False,
                "image": image_url,
                "output_format": output_format,
                "target_resolution": target_resolution
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            
            if response.status_code == 200:
                result = response.json()["data"]
                return result["id"], None
            else:
                return None, f"API Error: {response.status_code}, {response.text}"
                
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def submit_image_to_video_task(self, image_url, prompt, duration=5, negative_prompt="", 
                                 last_image="", seed=-1):
        """Submit image-to-video task to WaveSpeed AI"""
        try:
            url = f"{self.base_url}/wavespeed-ai/wan-2.2/i2v-480p"
            headers = self.get_headers()
            payload = {
                "duration": duration,
                "image": image_url,
                "last_image": last_image,
                "negative_prompt": negative_prompt,
                "prompt": prompt,
                "seed": seed
            }
            
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            
            if response.status_code == 200:
                result = response.json()["data"]
                return result["id"], None
            else:
                return None, f"API Error: {response.status_code}, {response.text}"
                
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def submit_seeddance_task(self, image_url, duration=5, prompt="", camera_fixed=False, seed=-1, version="480p"):
        """Submit SeedDance V1 Pro task (480p or 720p) to WaveSpeed AI"""
        try:
            logger.info(f"Submitting SeedDance V1 Pro {version} task with duration: {duration}s")
            
            # Select the appropriate endpoint based on version
            endpoint_key = f'seeddance_{version}' if version in ['480p', '720p'] else 'seeddance'
            url = Config.ENDPOINTS[endpoint_key]
            
            headers = self.get_headers()
            payload = {
                "prompt": prompt,
                "image": image_url,
                "duration": duration,
                "camera_fixed": camera_fixed,
                "seed": seed
            }
            
            response = self.session.post(url, headers=headers, 
                                       data=json.dumps(payload), 
                                       timeout=Config.TIMEOUT)
            
            if response.status_code == 200:
                result = response.json()["data"]
                request_id = result["id"]
                logger.log_api_request(f"seeddance_{version}", request_id, "submitted")
                return request_id, None
            else:
                error_msg = f"API Error: {response.status_code}, {response.text}"
                logger.error(error_msg)
                return None, error_msg
                
        except Exception as e:
            error_msg = f"Error submitting SeedDance V1 Pro task: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    def get_task_result(self, request_id):
        """Poll for task results"""
        try:
            url = f"{self.base_url}/predictions/{request_id}/result"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()["data"]
                return result, None
            else:
                return None, f"Polling error: {response.status_code}, {response.text}"
                
        except Exception as e:
            return None, f"Polling error: {str(e)}"
    
    def poll_until_complete(self, request_id, callback=None, poll_interval=1.0):
        """Poll for results until completion with optional progress callback"""
        start_time = time.time()
        
        while True:
            result, error = self.get_task_result(request_id)
            
            if error:
                return None, error, 0
            
            status = result["status"]
            
            if callback:
                callback(status, result)
            
            if status == "completed":
                end_time = time.time()
                duration = end_time - start_time
                output_url = result["outputs"][0] if result["outputs"] else None
                return output_url, None, duration
                
            elif status == "failed":
                error_msg = result.get('error', 'Unknown error')
                return None, f"Task failed: {error_msg}", 0
            
            time.sleep(poll_interval)
