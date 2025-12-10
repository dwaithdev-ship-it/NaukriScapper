"""AI integration module for webhook support and automated calling."""
import logging
import requests
from typing import Dict, Optional, List
from datetime import datetime

from config import DEFAULT_CALL_SCRIPT, N8N_WEBHOOK_URL, MAKE_WEBHOOK_URL, WEBHOOK_SECRET
from data_manager import DataManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AIIntegration:
    """Integration with AI tools like n8n and make.com for automated calling."""
    
    def __init__(self):
        """Initialize AI integration."""
        self.data_manager = DataManager()
    
    def format_call_script(self, candidate_data: Dict, job_data: Dict, template: Optional[str] = None) -> str:
        """
        Format the call script with candidate and job information.
        
        Args:
            candidate_data: Dictionary with candidate information
            job_data: Dictionary with job information
            template: Optional custom template, defaults to DEFAULT_CALL_SCRIPT
            
        Returns:
            Formatted script string
        """
        template = template or DEFAULT_CALL_SCRIPT
        
        try:
            script = template.format(
                candidate_name=candidate_data.get('name', 'Candidate'),
                job_role=job_data.get('job_role', 'a position'),
                experience_years=candidate_data.get('experience_years', 'N/A'),
                location=job_data.get('location', 'our office'),
                company_name=job_data.get('company_name', 'our company')
            )
            return script
        except KeyError as e:
            logger.warning(f"Missing key in template: {e}")
            return template
    
    def send_to_n8n(self, candidate_data: Dict, script: str) -> Dict:
        """
        Send candidate data to n8n webhook for automated calling.
        
        Args:
            candidate_data: Candidate information
            script: Call script to use
            
        Returns:
            Response from n8n webhook
        """
        if not N8N_WEBHOOK_URL:
            logger.warning("N8N_WEBHOOK_URL not configured")
            return {'error': 'N8N webhook URL not configured'}
        
        payload = {
            'candidate': candidate_data,
            'script': script,
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'naukri_scraper'
        }
        
        if WEBHOOK_SECRET:
            payload['secret'] = WEBHOOK_SECRET
        
        try:
            response = requests.post(
                N8N_WEBHOOK_URL,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            logger.info(f"Successfully sent candidate {candidate_data.get('name')} to n8n")
            return response.json() if response.content else {'status': 'success'}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending to n8n: {e}")
            return {'error': str(e)}
    
    def send_to_make(self, candidate_data: Dict, script: str) -> Dict:
        """
        Send candidate data to make.com webhook for automated calling.
        
        Args:
            candidate_data: Candidate information
            script: Call script to use
            
        Returns:
            Response from make.com webhook
        """
        if not MAKE_WEBHOOK_URL:
            logger.warning("MAKE_WEBHOOK_URL not configured")
            return {'error': 'Make.com webhook URL not configured'}
        
        payload = {
            'candidate': candidate_data,
            'script': script,
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'naukri_scraper'
        }
        
        if WEBHOOK_SECRET:
            payload['secret'] = WEBHOOK_SECRET
        
        try:
            response = requests.post(
                MAKE_WEBHOOK_URL,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            logger.info(f"Successfully sent candidate {candidate_data.get('name')} to make.com")
            return response.json() if response.content else {'status': 'success'}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending to make.com: {e}")
            return {'error': str(e)}
    
    def _validate_webhook_url(self, url: str) -> bool:
        """
        Validate webhook URL to prevent SSRF attacks.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is safe, False otherwise
        """
        from urllib.parse import urlparse
        from config import ALLOW_LOCAL_WEBHOOKS
        
        try:
            parsed = urlparse(url)
            
            # Only allow https and http schemes
            if parsed.scheme not in ['http', 'https']:
                logger.error(f"Invalid URL scheme: {parsed.scheme}")
                return False
            
            # Block private IP ranges and localhost (unless explicitly allowed for dev)
            hostname = parsed.hostname
            if not hostname:
                return False
            
            hostname_lower = hostname.lower()
            
            # Check for localhost/private IPs
            is_localhost = any(hostname_lower.startswith(h) for h in [
                'localhost', '127.0.0.1', '0.0.0.0', '169.254.', '::1', 'fe80:'
            ])
            
            is_private = (
                hostname_lower.startswith('10.') or
                hostname_lower.startswith('192.168.') or
                any(hostname_lower.startswith(f'172.{i}.') for i in range(16, 32))
            )
            
            if is_localhost or is_private:
                if not ALLOW_LOCAL_WEBHOOKS:
                    logger.error(f"Blocked private/localhost address: {hostname}. Set ALLOW_LOCAL_WEBHOOKS=True for development.")
                    return False
                else:
                    logger.warning(f"Allowing private/localhost address for development: {hostname}")
            
            return True
        except Exception as e:
            logger.error(f"Error validating URL: {e}")
            return False
    
    def send_to_webhook(self, webhook_url: str, candidate_data: Dict, script: str) -> Dict:
        """
        Send candidate data to a custom webhook URL.
        
        Args:
            webhook_url: Custom webhook URL (must be https/http and not private IP)
            candidate_data: Candidate information
            script: Call script to use
            
        Returns:
            Response from webhook
        """
        # Validate URL to prevent SSRF
        if not self._validate_webhook_url(webhook_url):
            return {'error': 'Invalid or unsafe webhook URL'}
        
        payload = {
            'candidate': candidate_data,
            'script': script,
            'timestamp': datetime.utcnow().isoformat(),
            'source': 'naukri_scraper'
        }
        
        if WEBHOOK_SECRET:
            payload['secret'] = WEBHOOK_SECRET
        
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            logger.info(f"Successfully sent candidate {candidate_data.get('name')} to {webhook_url}")
            return response.json() if response.content else {'status': 'success'}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending to webhook: {e}")
            return {'error': str(e)}
    
    def trigger_automated_calls(self,
                               candidate_ids: List[int],
                               job_data: Dict,
                               ai_tool: str = 'n8n',
                               custom_script: Optional[str] = None,
                               custom_webhook: Optional[str] = None):
        """
        Trigger automated calls for multiple candidates.
        
        Args:
            candidate_ids: List of candidate IDs to call
            job_data: Job information for script formatting
            ai_tool: Which AI tool to use ('n8n', 'make', or 'custom')
            custom_script: Optional custom call script template
            custom_webhook: Optional custom webhook URL (required if ai_tool='custom')
        """
        results = []
        
        for candidate_id in candidate_ids:
            try:
                # Get candidate from database
                from models import Candidate
                candidate = self.data_manager.session.query(Candidate).get(candidate_id)
                
                if not candidate:
                    logger.warning(f"Candidate {candidate_id} not found")
                    continue
                
                # Prepare candidate data
                candidate_data = {
                    'id': candidate.id,
                    'name': candidate.name,
                    'email': candidate.email,
                    'phone': candidate.phone,
                    'current_location': candidate.current_location,
                    'experience_years': candidate.experience_years,
                    'current_company': candidate.current_company,
                    'current_designation': candidate.current_designation,
                    'skills': candidate.skills
                }
                
                # Format script
                script = self.format_call_script(candidate_data, job_data, custom_script)
                
                # Send to appropriate webhook
                if ai_tool.lower() == 'n8n':
                    response = self.send_to_n8n(candidate_data, script)
                elif ai_tool.lower() == 'make':
                    response = self.send_to_make(candidate_data, script)
                elif ai_tool.lower() == 'custom' and custom_webhook:
                    response = self.send_to_webhook(custom_webhook, candidate_data, script)
                else:
                    logger.error(f"Invalid AI tool: {ai_tool}")
                    continue
                
                # Log the call
                call_status = 'sent' if 'error' not in response else 'failed'
                self.data_manager.log_call(
                    candidate_id=candidate_id,
                    script_used=script,
                    call_status=call_status,
                    ai_tool_used=ai_tool,
                    notes=str(response)
                )
                
                results.append({
                    'candidate_id': candidate_id,
                    'status': call_status,
                    'response': response
                })
                
            except Exception as e:
                logger.error(f"Error processing candidate {candidate_id}: {e}")
                results.append({
                    'candidate_id': candidate_id,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
    
    def process_webhook_response(self, webhook_data: Dict) -> Dict:
        """
        Process incoming webhook response from AI tools with call results.
        
        Args:
            webhook_data: Data received from webhook
            
        Returns:
            Processing result
        """
        try:
            candidate_id = webhook_data.get('candidate_id')
            call_status = webhook_data.get('call_status')
            interested = webhook_data.get('interested')
            response_text = webhook_data.get('response')
            
            if not candidate_id:
                return {'error': 'candidate_id is required'}
            
            # Update candidate status
            self.data_manager.update_candidate_status(
                candidate_id=candidate_id,
                contacted=True,
                interested=interested,
                comments=response_text
            )
            
            # Log the call result
            self.data_manager.log_call(
                candidate_id=candidate_id,
                script_used=webhook_data.get('script_used', ''),
                call_status=call_status or 'completed',
                interested=interested,
                ai_tool_used=webhook_data.get('ai_tool'),
                notes=response_text
            )
            
            logger.info(f"Processed webhook response for candidate {candidate_id}")
            return {'status': 'success', 'candidate_id': candidate_id}
            
        except Exception as e:
            logger.error(f"Error processing webhook response: {e}")
            return {'error': str(e)}
    
    def get_candidates_for_calling(self,
                                   job_search_id: int,
                                   contacted_only: bool = False,
                                   interested_only: bool = False) -> List[int]:
        """
        Get list of candidate IDs ready for calling.
        
        Args:
            job_search_id: Job search ID
            contacted_only: If True, return already contacted candidates; if False, return not yet contacted
            interested_only: Only return interested candidates
            
        Returns:
            List of candidate IDs
        """
        from models import Candidate
        
        query = self.data_manager.session.query(Candidate).filter(
            Candidate.job_search_id == job_search_id
        )
        
        if contacted_only:
            query = query.filter(Candidate.contacted.is_(True))
        else:
            query = query.filter(Candidate.contacted.is_(False))
        
        if interested_only:
            query = query.filter(Candidate.interested.is_(True))
        
        candidates = query.all()
        return [c.id for c in candidates]


if __name__ == '__main__':
    # Example usage
    ai = AIIntegration()
    
    # Example candidate and job data
    candidate_data = {
        'name': 'John Doe',
        'phone': '+91-9876543210',
        'experience_years': 3.5
    }
    
    job_data = {
        'job_role': 'Python Developer',
        'location': 'Bangalore',
        'company_name': 'Tech Corp'
    }
    
    # Format script
    script = ai.format_call_script(candidate_data, job_data)
    print("Formatted script:")
    print(script)
    
    # Note: Actual webhook calls would require valid URLs configured
