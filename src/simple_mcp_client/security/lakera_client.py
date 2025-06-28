"""
Lakera Guard API client.

This module provides a client for interacting with the Lakera Guard API
to screen content for security threats.
"""

import logging
import os
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin

import requests
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class LakeraGuardRequest(BaseModel):
    """Model for Lakera Guard API requests."""
    
    messages: List[Dict[str, str]] = Field(..., description="Messages to screen")
    dev_info: Optional[bool] = Field(default=False, description="Include developer info")


class LakeraGuardResponse(BaseModel):
    """Model for Lakera Guard API responses."""
    
    flagged: bool = Field(..., description="Whether the content was flagged")
    categories: Dict[str, bool] = Field(default_factory=dict, description="Category flags")
    category_scores: Dict[str, float] = Field(default_factory=dict, description="Category scores")
    dev_info: Optional[Dict[str, Any]] = Field(default=None, description="Developer info")


class LakeraClient:
    """
    Client for interacting with the Lakera Guard API.
    
    This client provides methods to screen content for various security threats
    including prompt injection, jailbreaking, and other malicious content.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.lakera.ai/v2",
        region: Optional[str] = None,
        timeout: int = 30
    ):
        """
        Initialize the Lakera client.
        
        Args:
            api_key: Lakera API key (defaults to LAKERA_GUARD_API_KEY env var)
            base_url: Base URL for the Lakera API
            region: Specific region to use (us-east-1, us-west-2, eu-west-1, ap-southeast-1)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv("LAKERA_GUARD_API_KEY")
        if not self.api_key:
            raise ValueError("Lakera API key is required. Set LAKERA_GUARD_API_KEY environment variable or pass api_key parameter.")
        
        # Set up base URL based on region
        if region:
            self.base_url = f"https://{region}.api.lakera.ai/v2"
        else:
            self.base_url = base_url
        
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        })
    
    def screen_content(
        self,
        content: Union[str, List[Dict[str, str]]],
        include_dev_info: bool = False
    ) -> LakeraGuardResponse:
        """
        Screen content for security threats.
        
        Args:
            content: Content to screen (string or list of message dicts)
            include_dev_info: Whether to include developer info in response
            
        Returns:
            LakeraGuardResponse with screening results
            
        Raises:
            requests.RequestException: If the API request fails
        """
        # Convert string content to message format
        if isinstance(content, str):
            messages = [{"role": "user", "content": content}]
        else:
            messages = content
        
        request_data = LakeraGuardRequest(
            messages=messages,
            dev_info=include_dev_info
        )
        
        try:
            response = self.session.post(
                urljoin(self.base_url, "/guard"),
                json=request_data.model_dump(exclude_none=True),
                timeout=self.timeout
            )
            response.raise_for_status()
            
            response_data = response.json()
            return LakeraGuardResponse(**response_data)
            
        except requests.RequestException as e:
            logger.error(f"Lakera Guard API request failed: {e}")
            raise
    
    def screen_tool_description(self, description: str) -> LakeraGuardResponse:
        """
        Screen a tool description for security threats.
        
        Args:
            description: Tool description to screen
            
        Returns:
            LakeraGuardResponse with screening results
        """
        return self.screen_content(description)
    
    def screen_server_interaction(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None
    ) -> LakeraGuardResponse:
        """
        Screen a server interaction for security threats.
        
        Args:
            method: MCP method being called
            params: Parameters being sent to the server
            
        Returns:
            LakeraGuardResponse with screening results
        """
        # Create a representation of the interaction for screening
        interaction_text = f"Method: {method}"
        if params:
            interaction_text += f"\nParameters: {str(params)}"
        
        return self.screen_content(interaction_text)
    
    def is_content_safe(self, content: Union[str, List[Dict[str, str]]]) -> bool:
        """
        Check if content is safe (not flagged by Lakera Guard).
        
        Args:
            content: Content to check
            
        Returns:
            True if content is safe, False if flagged
        """
        try:
            response = self.screen_content(content)
            return not response.flagged
        except Exception as e:
            logger.warning(f"Failed to screen content for safety: {e}")
            # Default to unsafe if screening fails
            return False
    
    def get_threat_categories(self, content: Union[str, List[Dict[str, str]]]) -> Dict[str, bool]:
        """
        Get detailed threat categories for content.
        
        Args:
            content: Content to analyze
            
        Returns:
            Dictionary mapping category names to boolean flags
        """
        try:
            response = self.screen_content(content)
            return response.categories
        except Exception as e:
            logger.warning(f"Failed to get threat categories: {e}")
            return {}
    
    def close(self):
        """Close the client session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 