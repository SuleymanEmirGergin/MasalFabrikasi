"""
Input Sanitization Utilities - XSS ve SQL Injection koruması
"""
import re
import html
from typing import Any, Dict


class InputSanitizer:
    """Input sanitization and validation"""
    
    # Dangerous patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|;|\/\*|\*\/)",
        r"(\bunion\b.*\bselect\b)",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
    ]
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 10000) -> str:
        """
        Sanitize a string input
        
        Args:
            value: Input string
            max_length: Maximum allowed length
        
        Returns:
            Sanitized string
        """
        if not isinstance(value, str):
            return str(value)
        
        # Trim to max length
        value = value[:max_length]
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # HTML escape
        value = html.escape(value)
        
        # Strip leading/trailing whitespace
        value = value.strip()
        
        return value
    
    @staticmethod
    def check_sql_injection(value: str) -> bool:
        """
        Check if string contains SQL injection patterns
        
        Returns:
            True if potentially malicious
        """
        value_lower = value.lower()
        
        for pattern in InputSanitizer.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def check_xss(value: str) -> bool:
        """
        Check if string contains XSS patterns
        
        Returns:
            True if potentially malicious
        """
        value_lower = value.lower()
        
        for pattern in InputSanitizer.XSS_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def sanitize_dict(data: Dict[str, Any], max_string_length: int = 10000) -> Dict[str, Any]:
        """
        Recursively sanitize all string values in a dictionary
        
        Args:
            data: Input dictionary
            max_string_length: Max length for strings
        
        Returns:
            Sanitized dictionary
        """
        sanitized = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                sanitized[key] = InputSanitizer.sanitize_string(value, max_string_length)
            elif isinstance(value, dict):
                sanitized[key] = InputSanitizer.sanitize_dict(value, max_string_length)
            elif isinstance(value, list):
                sanitized[key] = [
                    InputSanitizer.sanitize_string(item, max_string_length)
                    if isinstance(item, str) else item
                    for item in value
                ]
            else:
                sanitized[key] = value
        
        return sanitized
    
    @staticmethod
    def validate_and_sanitize(
        value: str,
        allow_html: bool = False,
        max_length: int = 10000
    ) -> str:
        """
        Validate and sanitize input
        
        Raises:
            ValueError if input contains malicious patterns
        """
        # Check for SQL injection
        if InputSanitizer.check_sql_injection(value):
            raise ValueError("Input contains potentially malicious SQL patterns")
        
        # Check for XSS (only if HTML not allowed)
        if not allow_html and InputSanitizer.check_xss(value):
            raise ValueError("Input contains potentially malicious XSS patterns")
        
        # Sanitize
        return InputSanitizer.sanitize_string(value, max_length)
