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
from typing import Optional, Tuple, Callable
from app.config import Config
from core.logger import get_logger

logger = get_logger()


class WaveSpeedAPIClient:
    """Client for interacting with WaveSpeed AI APIs"""
    
    def __init__(self):
        self.api_key = Config.API_KEY
        self.base_url = Config.BASE_URL
        self.session = requests.Session()  # Reuse connections
        self.session.headers.update({
            'User-Agent': 'WaveSpeedAI-GUI/2.0'
        })
        
    def get_headers(self, content_type="application/json"):
        """Get standard headers for API requests"""
        return {
            "Content-Type": content_type,
            "Authorization": f"Bearer {self.api_key}",
        }
    
    def convert_image_to_base64(self, image_path):
        """Convert image file to base64 string"""
        try:
            with Image.open(image_path) as img:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                
                image_base64 = base64.b64encode(buffer.getvalue()).decode()
                return image_base64
                
        except Exception as e:
            print(f"Error converting image to base64: {e}")
            return None
    
    def get_balance(self):
        """Get account balance from WaveSpeed AI API"""
        try:
            url = Config.ENDPOINTS['balance']
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            logger.info(f"Fetching account balance from: {url}")
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
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
                error_msg = f"HTTP {response.status_code}: {response.text}"
                logger.error(f"Balance API request failed: {error_msg}")
                return None, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = "Balance request timed out"
            logger.error(error_msg)
            return None, error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f"Balance request failed: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
        except Exception as e:
            error_msg = f"Unexpected error getting balance: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    def submit_image_edit_task(self, image_path, prompt, output_format="png"):
        """Submit image editing task to WaveSpeed AI"""
        try:
            logger.info(f"Submitting image edit task for: {image_path}")
            
            # Convert image to base64
            image_base64 = self.convert_image_to_base64(image_path)
            if not image_base64:
                error_msg = "Failed to convert image to base64"
                logger.error(error_msg)
                return None, error_msg
            
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
            
            if response.status_code == 200:
                result = response.json()["data"]
                request_id = result["id"]
                logger.log_api_request("image_edit", request_id, "submitted")
                return request_id, None
            else:
                error_msg = f"API Error: {response.status_code}, {response.text}"
                logger.error(error_msg)
                return None, error_msg
                
        except Exception as e:
            error_msg = f"Error submitting image edit task: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
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
    
    def submit_seedream_v4_task(self, image_url, prompt, size="2048*2048", seed=-1):
        """Submit Seedream V4 image editing task to WaveSpeed AI"""
        try:
            logger.info(f"Submitting Seedream V4 task with prompt: {prompt[:50]}...")
            
            url = Config.ENDPOINTS['seedream_v4']
            headers = self.get_headers()
            payload = {
                "prompt": prompt,
                "images": [image_url],  # Note: images is an array for Seedream V4
                "size": size,
                "seed": seed,
                "enable_sync_mode": False,
                "enable_base64_output": False
            }
            
            response = self.session.post(url, headers=headers, 
                                       data=json.dumps(payload), 
                                       timeout=Config.TIMEOUT)
            
            if response.status_code == 200:
                result = response.json()["data"]
                request_id = result["id"]
                logger.log_api_request("seedream_v4", request_id, "submitted")
                return request_id, None
            else:
                error_msg = f"API Error: {response.status_code}, {response.text}"
                logger.error(error_msg)
                return None, error_msg
                
        except Exception as e:
            error_msg = f"Error submitting Seedream V4 task: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
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
    
    def submit_seeddance_task(self, image_url, duration=5, prompt="", camera_fixed=True, seed=-1):
        """Submit SeedDance image-to-video task to WaveSpeed AI"""
        try:
            logger.info(f"Submitting SeedDance task with duration: {duration}s")
            
            url = Config.ENDPOINTS['seeddance']
            headers = self.get_headers()
            payload = {
                "camera_fixed": camera_fixed,
                "duration": duration,
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
                logger.log_api_request("seeddance", request_id, "submitted")
                return request_id, None
            else:
                error_msg = f"API Error: {response.status_code}, {response.text}"
                logger.error(error_msg)
                return None, error_msg
                
        except Exception as e:
            error_msg = f"Error submitting SeedDance task: {str(e)}"
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
