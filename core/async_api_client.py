"""
Async API Client for WaveSpeed AI Application

This module provides async API functionality for better responsiveness
and non-blocking operations.
"""

import asyncio
import aiohttp
import json
import base64
import io
from typing import Optional, Tuple, Dict, Any, Union, AsyncGenerator
from pathlib import Path
from PIL import Image

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


class AsyncWaveSpeedAPIClient:
    """Async client for interacting with WaveSpeed AI APIs"""
    
    def __init__(self) -> None:
        # Validate API key on initialization
        is_valid, error = validate_api_key(Config.API_KEY)
        if not is_valid:
            raise AuthenticationError(f"Invalid API key: {error}")
        
        self.api_key: ApiKey = Config.API_KEY
        self.base_url: str = Config.BASE_URL
        self.timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(total=Config.TIMEOUT)
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
    
    async def _ensure_session(self) -> None:
        """Ensure HTTP session is created"""
        if self._session is None or self._session.closed:
            headers = {
                'User-Agent': 'WaveSpeedAI-GUI/2.0',
                'Authorization': f'Bearer {self.api_key}'
            }
            self._session = aiohttp.ClientSession(
                headers=headers,
                timeout=self.timeout
            )
    
    async def close(self) -> None:
        """Close the HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    def get_headers(self, content_type: str = "application/json") -> Dict[str, str]:
        """Get standard headers for API requests"""
        return {
            "Content-Type": content_type,
            "Authorization": f"Bearer {self.api_key}",
        }
    
    async def convert_image_to_base64(self, image_path: Union[str, Path], preserve_colors: bool = True) -> Optional[str]:
        """
        Convert image file to base64 string asynchronously
        
        Args:
            image_path: Path to the image file
            preserve_colors: If True, reads file directly without color conversion (preserves original colors)
        """
        try:
            # Validate image file first
            is_valid, error = validate_image_file(image_path)
            if not is_valid:
                raise ImageProcessingError(f"Invalid image file: {error}", str(image_path))
            
            # Run image processing in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            image_base64 = await loop.run_in_executor(
                None, self._process_image_sync, image_path, preserve_colors
            )
            logger.info(f"Image encoded {'directly (colors preserved)' if preserve_colors else 'with conversion'}")
            return image_base64
                
        except ImageProcessingError:
            raise
        except Exception as e:
            raise ImageProcessingError(f"Error converting image to base64: {str(e)}", str(image_path))
    
    def _process_image_sync(self, image_path: Union[str, Path], preserve_colors: bool = True) -> str:
        """
        Synchronous image processing (runs in thread pool)
        
        Args:
            image_path: Path to the image file
            preserve_colors: If True, reads file directly without color conversion
        """
        if preserve_colors:
            # Direct file reading - preserves original colors perfectly
            with open(image_path, 'rb') as f:
                image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode()
            return image_base64
        else:
            # Legacy method with color conversion
            with Image.open(image_path) as img:
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                buffer = io.BytesIO()
                img.save(buffer, format="PNG")
                
                image_base64 = base64.b64encode(buffer.getvalue()).decode()
                return image_base64
    
    async def get_balance(self) -> Tuple[Optional[Balance], Optional[str]]:
        """Get account balance from WaveSpeed AI API asynchronously"""
        try:
            await self._ensure_session()
            url = Config.ENDPOINTS['balance']
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            
            logger.info(f"Fetching account balance from: {url}")
            
            async with self._session.get(url, headers=headers) as response:
                if response.status == HTTPStatusCodes.OK:
                    result = await response.json()
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
                    is_valid, error_msg = validate_http_status_code(response.status)
                    if not is_valid:
                        logger.error(f"Balance API request failed: {error_msg}")
                        return None, error_msg
                
        except asyncio.TimeoutError:
            raise handle_timeout_error(10.0, "Balance request timed out")
        except aiohttp.ClientError as e:
            raise handle_network_error(url, f"Balance request failed: {str(e)}")
        except Exception as e:
            raise APIError(f"Unexpected error getting balance: {str(e)}")
    
    async def submit_image_edit_task(self, image_path: Union[str, Path], prompt: str, output_format: str = "png") -> Tuple[Optional[RequestId], Optional[str]]:
        """Submit image editing task to WaveSpeed AI asynchronously"""
        try:
            # Validate inputs
            is_valid, error = validate_prompt(prompt)
            if not is_valid:
                raise handle_validation_error("prompt", prompt, error)
            
            is_valid, error = validate_output_format(output_format, "image")
            if not is_valid:
                raise handle_validation_error("output_format", output_format, error)
            
            logger.info(f"Submitting image edit task for: {image_path}")
            
            # Convert image to base64 (preserve colors by default)
            image_base64 = await self.convert_image_to_base64(image_path, preserve_colors=True)
            if not image_base64:
                raise ImageProcessingError("Failed to convert image to base64", str(image_path))
            
            # Detect original image format for proper MIME type
            img_path = Path(image_path)
            img_format = img_path.suffix.lower().lstrip('.')
            # Map common extensions to MIME types
            mime_map = {'jpg': 'jpeg', 'jpeg': 'jpeg', 'png': 'png', 'webp': 'webp', 'gif': 'gif'}
            mime_type = mime_map.get(img_format, 'png')
            
            await self._ensure_session()
            url = Config.ENDPOINTS['image_edit']
            headers = self.get_headers()
            payload = {
                "enable_base64_output": False,
                "enable_sync_mode": False,
                "images": [f"data:image/{mime_type};base64,{image_base64}"],
                "output_format": output_format,
                "prompt": prompt
            }
            
            async with self._session.post(url, headers=headers, json=payload) as response:
                if response.status == HTTPStatusCodes.OK:
                    result = await response.json()
                    request_id = result["data"]["id"]
                    logger.log_api_request("image_edit", request_id, "submitted")
                    return request_id, None
                else:
                    raise handle_api_error(response, url)
                
        except (ValidationError, ImageProcessingError, APIError):
            raise
        except Exception as e:
            raise APIError(f"Error submitting image edit task: {str(e)}")
    
    async def submit_seededit_task(self, image_url: str, prompt: str, guidance_scale: float = 0.5, seed: int = -1) -> Tuple[Optional[RequestId], Optional[str]]:
        """Submit SeedEdit image editing task to WaveSpeed AI asynchronously"""
        try:
            # Validate inputs
            is_valid, error = validate_prompt(prompt)
            if not is_valid:
                raise handle_validation_error("prompt", prompt, error)
            
            is_valid, error = validate_guidance_scale(guidance_scale)
            if not is_valid:
                raise handle_validation_error("guidance_scale", guidance_scale, error)
            
            is_valid, error = validate_seed(seed)
            if not is_valid:
                raise handle_validation_error("seed", seed, error)
            
            logger.info(f"Submitting SeedEdit task with prompt: {prompt[:50]}...")
            
            await self._ensure_session()
            url = Config.ENDPOINTS['seededit']
            headers = self.get_headers()
            payload = {
                "enable_base64_output": False,
                "guidance_scale": guidance_scale,
                "image": image_url,
                "prompt": prompt,
                "seed": seed
            }
            
            async with self._session.post(url, headers=headers, json=payload) as response:
                if response.status == HTTPStatusCodes.OK:
                    result = await response.json()
                    request_id = result["data"]["id"]
                    logger.log_api_request("seededit", request_id, "submitted")
                    return request_id, None
                else:
                    raise handle_api_error(response, url)
                
        except (ValidationError, APIError):
            raise
        except Exception as e:
            raise APIError(f"Error submitting SeedEdit task: {str(e)}")
    
    async def get_task_result(self, request_id: RequestId) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """Poll for task results asynchronously"""
        try:
            await self._ensure_session()
            url = f"{self.base_url}/predictions/{request_id}/result"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            async with self._session.get(url, headers=headers) as response:
                if response.status == HTTPStatusCodes.OK:
                    result = await response.json()
                    return result["data"], None
                else:
                    is_valid, error_msg = validate_http_status_code(response.status)
                    if not is_valid:
                        return None, error_msg
                    
        except asyncio.TimeoutError:
            raise handle_timeout_error(10.0, "Task result request timed out")
        except aiohttp.ClientError as e:
            raise handle_network_error(url, f"Task result request failed: {str(e)}")
        except Exception as e:
            raise APIError(f"Error getting task result: {str(e)}")
    
    async def poll_until_complete(self, request_id: RequestId, callback: Optional[callable] = None, poll_interval: float = 1.0) -> AsyncGenerator[Tuple[str, Dict[str, Any]], None]:
        """Poll for results until completion with optional progress callback asynchronously"""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            result, error = await self.get_task_result(request_id)
            
            if error:
                yield "error", {"error": error, "duration": 0}
                return
            
            status = result["status"]
            
            if callback:
                callback(status, result)
            
            yield status, result
            
            if status == "completed":
                end_time = asyncio.get_event_loop().time()
                duration = end_time - start_time
                yield "completed", {"result": result, "duration": duration}
                return
                
            elif status == "failed":
                error_msg = result.get('error', 'Unknown error')
                yield "failed", {"error": f"Task failed: {error_msg}", "duration": 0}
                return
            
            await asyncio.sleep(poll_interval)
    
    async def batch_submit_tasks(self, tasks: list) -> list:
        """Submit multiple tasks concurrently"""
        try:
            await self._ensure_session()
            
            # Create tasks for concurrent execution
            coroutines = []
            for task in tasks:
                if task['type'] == 'image_edit':
                    coro = self.submit_image_edit_task(
                        task['image_path'], 
                        task['prompt'], 
                        task.get('output_format', 'png')
                    )
                elif task['type'] == 'seededit':
                    coro = self.submit_seededit_task(
                        task['image_url'],
                        task['prompt'],
                        task.get('guidance_scale', 0.5),
                        task.get('seed', -1)
                    )
                else:
                    continue
                
                coroutines.append(coro)
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*coroutines, return_exceptions=True)
            
            # Process results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    processed_results.append({
                        'task_id': i,
                        'success': False,
                        'error': str(result)
                    })
                else:
                    request_id, error = result
                    processed_results.append({
                        'task_id': i,
                        'success': error is None,
                        'request_id': request_id,
                        'error': error
                    })
            
            return processed_results
            
        except Exception as e:
            raise APIError(f"Error in batch task submission: {str(e)}")


# Utility functions for async operations
async def run_async_api_call(coro):
    """Run async API call in a new event loop"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return await coro


def sync_wrapper(async_func):
    """Decorator to run async function synchronously"""
    def wrapper(*args, **kwargs):
        return asyncio.run(async_func(*args, **kwargs))
    return wrapper


# Example usage functions
async def example_async_usage():
    """Example of async API client usage"""
    async with AsyncWaveSpeedAPIClient() as client:
        # Get balance
        balance, error = await client.get_balance()
        if error:
            print(f"Error getting balance: {error}")
        else:
            print(f"Balance: ${balance}")
        
        # Submit image edit task
        request_id, error = await client.submit_image_edit_task(
            "path/to/image.png",
            "Make it more artistic"
        )
        
        if error:
            print(f"Error submitting task: {error}")
        else:
            print(f"Task submitted: {request_id}")
            
            # Poll for results
            async for status, data in client.poll_until_complete(request_id):
                print(f"Status: {status}")
                if status == "completed":
                    print(f"Task completed in {data['duration']:.2f} seconds")
                    break
                elif status == "failed":
                    print(f"Task failed: {data['error']}")
                    break


if __name__ == "__main__":
    # Example usage
    asyncio.run(example_async_usage())
