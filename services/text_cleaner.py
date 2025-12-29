"""Text cleaning utilities for research content"""

import re
import html
from typing import Optional


def clean_html_content(text: str) -> str:
    """
    Clean HTML and markdown artifacts from text content
    
    Args:
        text: Raw text that may contain HTML/markdown
        
    Returns:
        Cleaned, readable text
    """
    if not text:
        return ""
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Remove markdown artifacts
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)  # [text](url) -> text
    text = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', text)  # Remove images
    text = re.sub(r'```[^`]*```', '', text)  # Remove code blocks
    text = re.sub(r'`([^`]+)`', r'\1', text)  # Remove inline code markers
    
    # Remove common markdown/HTML artifacts
    text = re.sub(r'_{2,}', '', text)  # Remove underscores (markdown emphasis)
    text = re.sub(r'\*{2,}', '', text)  # Remove asterisks (markdown bold)
    text = re.sub(r'#{1,6}\s', '', text)  # Remove markdown headers
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)  # Multiple spaces to single space
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Multiple newlines to double newline
    
    # Remove common web artifacts
    text = re.sub(r'(Share|Tweet|Pin|Email|Print)\s*$', '', text, flags=re.IGNORECASE)
    text = re.sub(r'(Cookie|Privacy Policy|Terms of Service|Subscribe|Newsletter)', '', text, flags=re.IGNORECASE)
    
    # Clean up leading/trailing artifacts
    text = text.strip()
    text = re.sub(r'^[_\-\*\s]+', '', text)  # Remove leading artifacts
    text = re.sub(r'[_\-\*\s]+$', '', text)  # Remove trailing artifacts
    
    return text


def extract_clean_sentences(text: str, max_sentences: int = 5) -> str:
    """
    Extract clean, complete sentences from text
    
    Args:
        text: Raw text
        max_sentences: Maximum number of sentences to extract
        
    Returns:
        Clean text with complete sentences
    """
    if not text:
        return ""
    
    # Clean the text first
    text = clean_html_content(text)
    
    # Split into sentences (basic sentence detection)
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Filter out very short or incomplete sentences
    valid_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        # Keep sentences that are at least 20 chars and end with punctuation
        if len(sentence) >= 20 and sentence[-1] in '.!?':
            valid_sentences.append(sentence)
        
        if len(valid_sentences) >= max_sentences:
            break
    
    return ' '.join(valid_sentences)


def truncate_smart(text: str, max_length: int = 500) -> str:
    """
    Truncate text smartly at sentence boundaries
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        
    Returns:
        Truncated text ending at a sentence boundary
    """
    if not text or len(text) <= max_length:
        return text
    
    # Clean first
    text = clean_html_content(text)
    
    # Find the last sentence boundary before max_length
    truncated = text[:max_length]
    
    # Find last period, exclamation, or question mark
    last_period = max(truncated.rfind('.'), truncated.rfind('!'), truncated.rfind('?'))
    
    if last_period > max_length * 0.5:  # If we found a boundary in the latter half
        return truncated[:last_period + 1].strip()
    else:
        # No good boundary found, just truncate and add ellipsis
        return truncated.rsplit(' ', 1)[0] + '...'


def clean_competitive_landscape(text: str) -> str:
    """
    Clean competitive landscape text specifically
    
    Args:
        text: Raw competitive landscape text
        
    Returns:
        Cleaned competitor description
    """
    text = clean_html_content(text)
    
    # Remove common artifacts from competitor descriptions
    text = re.sub(r'(Company Profile|Overview|Report|IBISWorld|Access all)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'(Contact Us|Log in|Mobile Menu)', '', text, flags=re.IGNORECASE)
    text = re.sub(r'(Unlock|Membership|Subscribe)', '', text, flags=re.IGNORECASE)
    
    # Clean up
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text
