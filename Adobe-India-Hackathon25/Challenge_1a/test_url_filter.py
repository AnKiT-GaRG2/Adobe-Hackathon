import re

def contains_url(text):
    """
    Check if text contains URLs or web addresses
    Returns True if the text contains any URL patterns
    """
    if not text:
        return False
    
    # Define URL patterns
    url_patterns = [
        # Standard HTTP/HTTPS URLs
        r'https?://[^\s]+',
        
        # FTP URLs
        r'ftp://[^\s]+',
        
        # URLs without protocol
        r'www\.[^\s]+',
        
        # Domain patterns (like example.com)
        r'\b[a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.([a-zA-Z]{2,})\b',
        
        # Email addresses (often found with URLs)
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        
        # IP addresses
        r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        
        # File extensions commonly associated with web content
        r'\b[^\s]+\.(html?|php|asp|jsp|css|js)\b',
        
        # Common URL-like patterns
        r'\b[^\s]*://[^\s]*',
        
        # Domain-like patterns with common TLDs
        r'\b[^\s]+\.(com|org|net|edu|gov|mil|int|co|uk|de|fr|jp|cn|au|ca|in|br|mx|ru|za|it|es|nl|se|no|dk|fi|be|at|ch|pl|cz|hu|gr|pt|ie|il|kr|tw|hk|sg|th|my|id|ph|vn|pk|bd|lk|np|mm|kh|la|mn|uz|kz|kg|tj|tm|af|ir|iq|sa|ae|om|ye|jo|lb|sy|tr|cy|ge|az|am|by|ua|md|ro|bg|rs|hr|si|sk|lt|lv|ee|is|fo|gl|ad|sm|va|mc|li|lu|mt|al|mk|ba|me|xk|gg|je|im|gi|mq|gp|re|yt|nc|pf|wf|pm|bl|mf|sx|cw|aw|tc|ky|bm|vg|ai|ms|ag|bb|dm|gd|kn|lc|vc|tt|jm|ht|do|cu|bs|pr|vi|as|gu|mp|pw|fm|mh|ki|nr|tv|to|ws|vu|sb|fj|pg|nc|nf|ck|nu|tk|pn|gs|io|tf|bv|sj|um|aq)\b',
    ]
    
    # Check if any URL pattern matches the text
    for pattern in url_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False

# Test cases for URL detection
test_cases = [
    ("Chapter 1: Introduction", False),  # Normal heading
    ("Visit www.example.com", True),  # WWW URL
    ("https://github.com/user/repo", True),  # HTTPS URL
    ("Contact us at info@company.com", True),  # Email
    ("Server 192.168.1.1", True),  # IP address
    ("Download index.html", True),  # HTML file
    ("Documents and Web Sites", False),  # Should NOT be filtered - just mentions web sites
    ("Go to example.com for more", True),  # Domain
    ("FTP Server", False),  # Just mentions FTP
    ("ftp://files.example.com", True),  # Actual FTP URL
    ("See page.php?id=123", True),  # PHP file
    ("Web Development", False),  # Just mentions web
    ("Visit our site: company.org", True),  # Domain with colon
    ("Protocol://server/path", True),  # Generic protocol
]

print("Testing URL filtering function:")
print("=" * 50)
for text, expected in test_cases:
    result = contains_url(text)
    status = "✓" if result == expected else "✗"
    print(f"{status} '{text}' -> {result} (expected: {expected})")

print("\n" + "=" * 50)
print("URL filter test complete!")
