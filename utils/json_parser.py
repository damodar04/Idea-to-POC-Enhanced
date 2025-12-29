import json
import re
import logging
from typing import Any, Dict, List, Union

logger = logging.getLogger(__name__)

def extract_json_from_text(text: str, default: Any = None) -> Any:
    """
    Robustly extract JSON from text, handling markdown code blocks and extra text.
    
    Args:
        text: The text containing JSON
        default: Default value to return on failure
        
    Returns:
        Parsed JSON object (dict or list) or default value
    """
    if not text:
        return default

    # Try to find JSON within markdown code blocks
    json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if json_match:
        text = json_match.group(1)
    else:
        # Try to find code block without language specifier
        code_match = re.search(r'```\s*(.*?)\s*```', text, re.DOTALL)
        if code_match:
            text = code_match.group(1)

    # Clean up the text
    text = text.strip()
    
    # Attempt to parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # If simple parse fails, try to find the first '{' or '[' and the last '}' or ']'
        try:
            # Find start
            start_idx = -1
            if '{' in text:
                start_idx = text.find('{')
            
            if '[' in text:
                idx = text.find('[')
                if start_idx == -1 or (idx != -1 and idx < start_idx):
                    start_idx = idx
            
            if start_idx == -1:
                logger.warning(f"No JSON start found in text: {text[:100]}...")
                return default

            # Find end
            end_idx = -1
            last_brace = text.rfind('}')
            last_bracket = text.rfind(']')
            
            if last_brace > last_bracket:
                end_idx = last_brace + 1
            else:
                end_idx = last_bracket + 1
                
            if end_idx <= start_idx:
                logger.warning(f"No valid JSON range found in text")
                return default
                
            json_str = text[start_idx:end_idx]
            return json.loads(json_str)
            
        except Exception as e:
            logger.error(f"Failed to extract JSON: {e}")
            return default
