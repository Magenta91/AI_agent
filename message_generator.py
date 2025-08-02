import os
import logging
import google.generativeai as genai
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class MessageGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self._configure_gemini()
    
    def _configure_gemini(self):
        """Configure Gemini API with the provided API key."""
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Successfully configured Gemini API")
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {e}")
            raise
    
    def generate_message(self, lead: Dict) -> Optional[str]:
        """Generate a personalized outreach message for a lead using Gemini API."""
        try:
            prompt = self._create_prompt(lead)
            
            response = self.model.generate_content(prompt)
            
            if response.text:
                message = response.text.strip()
                logger.info(f"Generated message for {lead['name']}")
                return message
            else:
                logger.error(f"Empty response from Gemini for {lead['name']}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating message for {lead['name']}: {e}")
            return None
    
    def _create_prompt(self, lead: Dict) -> str:
        """Create the prompt template for Gemini API."""
        prompt = f"""You are an outreach assistant. Generate a friendly, professional WhatsApp or email message for a lead.

Lead Details:
- Name: {lead['name']}
- Region: {lead['region']}
- Interest: {lead['interest']}

Requirements:
1. Greet the lead by name.
2. Mention their interest and region naturally.
3. Keep it under 80 words.
4. End with a clear call to action.

Return ONLY the message."""
        
        return prompt
    
    def test_generation(self, sample_lead: Dict) -> str:
        """Test message generation with a sample lead."""
        logger.info("Testing message generation...")
        message = self.generate_message(sample_lead)
        if message:
            logger.info("Test successful!")
            return message
        else:
            logger.error("Test failed!")
            return "Test failed - no message generated"