import secrets
import string
from typing import Optional
from fastapi import Request
import re

def generate_api_key(length: int = 32) -> str:
    """Generate a secure API key"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def is_safe_url(url: str, allowed_hosts: Optional[list] = None) -> bool:
    """Check if a URL is safe for redirects"""
    if not url:
        return False
    
    # Check for absolute URLs
    if url.startswith(('http://', 'https://')):
        if allowed_hosts:
            import urllib.parse
            parsed = urllib.parse.urlparse(url)
            return parsed.netloc in allowed_hosts
        return False
    
    # Relative URLs are generally safer
    return url.startswith('/') and not url.startswith('//')

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove or escape potentially dangerous characters
    text = text.strip()
    text = text[:max_length]  # Limit length
    
    # Remove control characters except newlines and tabs
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
    
    return text

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def get_client_ip(request: Request) -> str:
    """Get client IP address from request"""
    # Check for forwarded headers (when behind a proxy)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Get the first IP in the chain
        return forwarded_for.split(",")[0].strip()
    
    forwarded = request.headers.get("X-Forwarded")
    if forwarded:
        return forwarded.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fallback to direct client IP
    return request.client.host if request.client else "unknown"

def is_suspicious_request(request: Request) -> bool:
    """Check for suspicious request patterns"""
    user_agent = request.headers.get("user-agent", "").lower()
    
    # Common bot patterns (extend as needed)
    suspicious_patterns = [
        "bot", "crawler", "spider", "scraper", 
        "wget", "curl", "python-requests"
    ]
    
    # Check for suspicious user agents
    for pattern in suspicious_patterns:
        if pattern in user_agent:
            return True
    
    # Check for missing common headers
    if not request.headers.get("accept"):
        return True
    
    return False

class SecurityValidator:
    """Security validation utilities"""
    
    @staticmethod
    def validate_password_strength(password: str) -> dict:
        """Validate password strength"""
        result = {
            "valid": True,
            "score": 0,
            "issues": []
        }
        
        if len(password) < 8:
            result["valid"] = False
            result["issues"].append("Password must be at least 8 characters")
        else:
            result["score"] += 1
        
        if not re.search(r"[A-Z]", password):
            result["valid"] = False
            result["issues"].append("Password must contain uppercase letters")
        else:
            result["score"] += 1
        
        if not re.search(r"[a-z]", password):
            result["valid"] = False
            result["issues"].append("Password must contain lowercase letters")
        else:
            result["score"] += 1
        
        if not re.search(r"\d", password):
            result["valid"] = False
            result["issues"].append("Password must contain numbers")
        else:
            result["score"] += 1
        
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password):
            result["issues"].append("Password should contain special characters")
        else:
            result["score"] += 1
        
        return result
    
    @staticmethod
    def validate_username(username: str) -> dict:
        """Validate username"""
        result = {
            "valid": True,
            "issues": []
        }
        
        if len(username) < 3:
            result["valid"] = False
            result["issues"].append("Username must be at least 3 characters")
        
        if len(username) > 50:
            result["valid"] = False
            result["issues"].append("Username must be less than 50 characters")
        
        if not re.match(r"^[a-zA-Z0-9_-]+$", username):
            result["valid"] = False
            result["issues"].append("Username can only contain letters, numbers, underscores, and hyphens")
        
        return result
