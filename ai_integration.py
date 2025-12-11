"""AI integration with webhook support for n8n, make.com, and custom webhooks."""
import requests
import json
import re
import ipaddress
from typing import Dict, Optional, Any
from urllib.parse import urlparse
from config import Config
from data_manager import DataManager


class AIIntegration:
    """Handles AI integration via webhooks with SSRF protection."""
    
    def __init__(self):
        """Initialize AI integration."""
        self.webhook_url = Config.WEBHOOK_URL
        self.n8n_url = Config.N8N_WEBHOOK_URL
        self.make_url = Config.MAKE_WEBHOOK_URL
        self.allow_local = Config.ALLOW_LOCAL_WEBHOOKS
        self.data_manager = DataManager()
    
    def send_to_n8n(self, data: Dict) -> Dict:
        """Send data to n8n webhook.
        
        Args:
            data: Data to send
            
        Returns:
            Response data
        """
        if not self.n8n_url:
            return {'error': 'n8n webhook URL not configured'}
        
        return self._send_webhook(self.n8n_url, data)
    
    def send_to_make(self, data: Dict) -> Dict:
        """Send data to make.com webhook.
        
        Args:
            data: Data to send
            
        Returns:
            Response data
        """
        if not self.make_url:
            return {'error': 'Make.com webhook URL not configured'}
        
        return self._send_webhook(self.make_url, data)
    
    def send_to_custom_webhook(self, data: Dict, webhook_url: str = None) -> Dict:
        """Send data to custom webhook.
        
        Args:
            data: Data to send
            webhook_url: Custom webhook URL (uses default if not provided)
            
        Returns:
            Response data
        """
        url = webhook_url or self.webhook_url
        if not url:
            return {'error': 'Webhook URL not provided'}
        
        return self._send_webhook(url, data)
    
    def _send_webhook(self, url: str, data: Dict) -> Dict:
        """Send data to webhook with validation.
        
        Args:
            url: Webhook URL
            data: Data to send
            
        Returns:
            Response data
        """
        # Validate webhook URL for SSRF protection
        if not self._validate_webhook_url(url):
            return {
                'error': 'Invalid webhook URL - blocked for security reasons',
                'details': 'URL contains private IP or localhost. Set ALLOW_LOCAL_WEBHOOKS=True for development.'
            }
        
        try:
            response = requests.post(
                url,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            response.raise_for_status()
            
            return {
                'success': True,
                'status_code': response.status_code,
                'response': response.json() if response.content else {}
            }
        except requests.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _validate_webhook_url(self, url: str) -> bool:
        """Validate webhook URL to prevent SSRF attacks.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid and safe
        """
        if not url:
            return False
        
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme not in ['http', 'https']:
                return False
            
            # Check hostname
            hostname = parsed.hostname
            if not hostname:
                return False
            
            # Allow bypass for local development
            if self.allow_local:
                return True
            
            # Block localhost variations
            localhost_patterns = [
                'localhost',
                '127.0.0.1',
                '0.0.0.0',
                '::1',
                'local',
            ]
            
            if any(pattern in hostname.lower() for pattern in localhost_patterns):
                return False
            
            # Try to resolve to IP and check if it's private
            try:
                import socket
                ip = socket.gethostbyname(hostname)
                ip_obj = ipaddress.ip_address(ip)
                
                # Block private IPs
                if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local:
                    return False
            except (socket.gaierror, ValueError):
                # If we can't resolve, allow it (might be valid external domain)
                pass
            
            return True
            
        except Exception:
            return False
    
    def send_candidate_data(self, candidate_id: int, webhook_type: str = 'custom') -> Dict:
        """Send candidate data to webhook.
        
        Args:
            candidate_id: ID of the candidate
            webhook_type: Type of webhook ('n8n', 'make', or 'custom')
            
        Returns:
            Response data
        """
        candidate = self.data_manager.get_candidate(candidate_id)
        if not candidate:
            return {'error': f'Candidate {candidate_id} not found'}
        
        data = candidate.to_dict()
        
        if webhook_type == 'n8n':
            return self.send_to_n8n(data)
        elif webhook_type == 'make':
            return self.send_to_make(data)
        else:
            return self.send_to_custom_webhook(data)
    
    def process_webhook_callback(self, data: Dict) -> Dict:
        """Process callback from webhook.
        
        Args:
            data: Callback data
            
        Returns:
            Processing result
        """
        # Extract candidate_id and call information
        candidate_id = data.get('candidate_id')
        call_status = data.get('call_status', 'unknown')
        duration = data.get('duration', 0)
        notes = data.get('notes', '')
        success = data.get('success', False)
        
        if not candidate_id:
            return {'error': 'candidate_id required'}
        
        # Create call log
        call_log = self.data_manager.create_call_log(
            candidate_id=candidate_id,
            call_status=call_status,
            duration=duration,
            notes=notes,
            webhook_response=json.dumps(data),
            success=success
        )
        
        return {
            'success': True,
            'call_log_id': call_log.id,
            'message': 'Callback processed successfully'
        }
    
    def get_webhook_config(self) -> Dict:
        """Get webhook configuration.
        
        Returns:
            Webhook configuration
        """
        return {
            'webhook_url': self.webhook_url if self.webhook_url else None,
            'n8n_url': self.n8n_url if self.n8n_url else None,
            'make_url': self.make_url if self.make_url else None,
            'allow_local_webhooks': self.allow_local
        }
