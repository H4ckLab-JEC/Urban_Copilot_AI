"""Utilities for API operations"""

import httpx
import asyncio
from typing import Optional, Dict, Any

async def get_with_retry(
    url: str, 
    max_retries: int = 3,
    timeout: float = 10.0
) -> Optional[Dict[str, Any]]:
    """
    Make HTTP GET request with retry logic
    
    Args:
        url: API endpoint
        max_retries: Number of retry attempts
        timeout: Request timeout in seconds
    
    Returns:
        Response JSON or None if failed
    """
    async with httpx.AsyncClient() as client:
        for attempt in range(max_retries):
            try:
                response = await client.get(url, timeout=timeout)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)
    return None
