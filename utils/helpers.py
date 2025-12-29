import uuid
from datetime import datetime

def generate_session_id():
    """Generate a unique session ID"""
    return str(uuid.uuid4())

def format_datetime(dt: datetime) -> str:
    """Format datetime for display"""
    if isinstance(dt, str):
        return dt
    return dt.strftime("%Y-%m-%d %H:%M:%S") if dt else "N/A"

def get_initials(name: str) -> str:
    """Get initials from name"""
    parts = name.split()
    return "".join([p[0].upper() for p in parts if p])

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length"""
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text

def format_score(score: int) -> str:
    """Format score with color-coded quality"""
    if score >= 80:
        return f"🟢 {score}/100 (Excellent)"
    elif score >= 60:
        return f"🟡 {score}/100 (Good)"
    elif score >= 40:
        return f"🟠 {score}/100 (Fair)"
    else:
        return f"🔴 {score}/100 (Poor)"
