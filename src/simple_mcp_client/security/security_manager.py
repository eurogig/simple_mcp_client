"""
Security manager for MCP client interactions.

This module provides a security manager that integrates Lakera Guard
screening into the MCP client workflow.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from .lakera_client import LakeraClient, LakeraGuardResponse

logger = logging.getLogger(__name__)


class SecurityViolation(Exception):
    """Exception raised when security screening detects a threat."""
    
    def __init__(self, message: str, categories: Dict[str, bool], scores: Dict[str, float]):
        super().__init__(message)
        self.categories = categories
        self.scores = scores


class SecurityManager:
    """
    Security manager for MCP client interactions.
    
    This manager integrates Lakera Guard screening to ensure safe
    interactions with MCP servers.
    """
    
    def __init__(
        self,
        lakera_client: Optional[LakeraClient] = None,
        enable_tool_screening: bool = True,
        enable_interaction_screening: bool = True,
        fail_on_violation: bool = True
    ):
        """
        Initialize the security manager.
        
        Args:
            lakera_client: Lakera client instance (will create one if not provided)
            enable_tool_screening: Whether to screen tool descriptions
            enable_interaction_screening: Whether to screen server interactions
            fail_on_violation: Whether to raise exceptions on security violations
        """
        self.lakera_client = lakera_client or LakeraClient()
        self.enable_tool_screening = enable_tool_screening
        self.enable_interaction_screening = enable_interaction_screening
        self.fail_on_violation = fail_on_violation
        
        # Track screening statistics
        self.screening_stats = {
            "tools_screened": 0,
            "interactions_screened": 0,
            "violations_detected": 0,
            "screening_errors": 0
        }
    
    def screen_tool_registration(
        self,
        tool_name: str,
        tool_description: str,
        tool_parameters: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Screen a tool during registration.
        
        Args:
            tool_name: Name of the tool
            tool_description: Description of the tool
            tool_parameters: Tool parameters schema
            
        Returns:
            True if tool is safe, False if flagged
            
        Raises:
            SecurityViolation: If tool is flagged and fail_on_violation is True
        """
        if not self.enable_tool_screening:
            return True
        
        try:
            # Create comprehensive tool representation for screening
            tool_content = f"Tool: {tool_name}\nDescription: {tool_description}"
            if tool_parameters:
                tool_content += f"\nParameters: {str(tool_parameters)}"
            
            response = self.lakera_client.screen_tool_description(tool_content)
            self.screening_stats["tools_screened"] += 1
            
            if response.flagged:
                self.screening_stats["violations_detected"] += 1
                violation_msg = f"Tool '{tool_name}' flagged by security screening"
                
                if self.fail_on_violation:
                    raise SecurityViolation(
                        violation_msg,
                        response.categories,
                        response.category_scores
                    )
                else:
                    logger.warning(f"{violation_msg}. Categories: {response.categories}")
                    return False
            
            return True
            
        except Exception as e:
            self.screening_stats["screening_errors"] += 1
            if isinstance(e, SecurityViolation):
                raise
            else:
                logger.error(f"Error screening tool '{tool_name}': {e}")
                # Default to safe if screening fails
                return True
    
    def screen_server_interaction(
        self,
        method: str,
        params: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Screen a server interaction.
        
        Args:
            method: MCP method being called
            params: Parameters being sent to the server
            response_data: Response data from the server
            
        Returns:
            True if interaction is safe, False if flagged
            
        Raises:
            SecurityViolation: If interaction is flagged and fail_on_violation is True
        """
        if not self.enable_interaction_screening:
            return True
        
        try:
            # Screen the request
            request_response = self.lakera_client.screen_server_interaction(method, params)
            
            # Screen the response if provided
            response_response = None
            if response_data:
                response_text = f"Response for {method}: {str(response_data)}"
                response_response = self.lakera_client.screen_content(response_text)
            
            self.screening_stats["interactions_screened"] += 1
            
            # Check for violations
            request_flagged = request_response.flagged
            response_flagged = response_response.flagged if response_response else False
            
            if request_flagged or response_flagged:
                self.screening_stats["violations_detected"] += 1
                violation_msg = f"Server interaction flagged by security screening"
                
                if request_flagged:
                    violation_msg += f" (request: {request_response.categories})"
                if response_flagged:
                    violation_msg += f" (response: {response_response.categories})"
                
                if self.fail_on_violation:
                    # Use request response for exception details
                    raise SecurityViolation(
                        violation_msg,
                        request_response.categories,
                        request_response.category_scores
                    )
                else:
                    logger.warning(violation_msg)
                    return False
            
            return True
            
        except Exception as e:
            self.screening_stats["screening_errors"] += 1
            if isinstance(e, SecurityViolation):
                raise
            else:
                logger.error(f"Error screening server interaction: {e}")
                # Default to safe if screening fails
                return True
    
    def screen_tools_list(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Screen a list of tools and filter out unsafe ones.
        
        Args:
            tools: List of tools to screen
            
        Returns:
            Filtered list of safe tools
        """
        if not self.enable_tool_screening:
            return tools
        
        safe_tools = []
        
        for tool in tools:
            tool_name = tool.get("name", "Unknown")
            tool_description = tool.get("description", "")
            tool_parameters = tool.get("parameters")
            
            try:
                if self.screen_tool_registration(tool_name, tool_description, tool_parameters):
                    safe_tools.append(tool)
                else:
                    logger.info(f"Tool '{tool_name}' filtered out due to security concerns")
            except SecurityViolation:
                logger.info(f"Tool '{tool_name}' filtered out due to security violation")
                # Continue processing other tools
        
        return safe_tools
    
    def get_screening_stats(self) -> Dict[str, int]:
        """
        Get screening statistics.
        
        Returns:
            Dictionary with screening statistics
        """
        return self.screening_stats.copy()
    
    def reset_stats(self):
        """Reset screening statistics."""
        self.screening_stats = {
            "tools_screened": 0,
            "interactions_screened": 0,
            "violations_detected": 0,
            "screening_errors": 0
        }
    
    def close(self):
        """Close the security manager and underlying Lakera client."""
        if self.lakera_client:
            self.lakera_client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 