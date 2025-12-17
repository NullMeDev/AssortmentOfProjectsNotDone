#!/usr/bin/env python3
"""
Enhanced Credential Formatter for SkyBin
Ensures proper formatting of scraped data according to specifications
"""

import re
from typing import List, Dict, Tuple, Optional
from collections import Counter, defaultdict
import hashlib

class EnhancedCredentialFormatter:
    """Formats credentials according to the exact specification required"""
    
    # Service name mappings for consistent naming
    SERVICE_NAMES = {
        'netflix': 'Netflix',
        'disney': 'Disney+', 
        'hbo': 'HBO Max',
        'amazon': 'Amazon Prime',
        'spotify': 'Spotify',
        'nordvpn': 'NordVPN',
        'expressvpn': 'ExpressVPN',
        'steam': 'Steam',
        'fortnite': 'Fortnite',
        'minecraft': 'Minecraft',
        'roblox': 'Roblox',
        'gmail': 'Gmail',
        'outlook': 'Outlook',
        'paypal': 'PayPal',
        'aws': 'AWS',
        'github': 'GitHub',
        'discord': 'Discord',
        'telegram': 'Telegram',
        'api': 'API Key',
        'ssh': 'SSH Key',
        'private': 'Private Key'
    }
    
    # Patterns for different credential types
    PATTERNS = {
        'email_pass': re.compile(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)[:\s]+([^\s:]{4,})', re.IGNORECASE),
        'user_pass': re.compile(r'(?:user(?:name)?|login)[:\s]*([^\s:]+)[:\s]+(?:pass(?:word)?)[:\s]*([^\s:]+)', re.IGNORECASE),
        'url_login_pass': re.compile(r'(https?://[^\s]+)\s+([^\s@]+)\s+([^\s]{4,})', re.IGNORECASE),
        'api_key_generic': re.compile(r'(?:api[_\s]?key|token)[:\s]*([a-zA-Z0-9_-]{20,})', re.IGNORECASE),
        'github_pat': re.compile(r'ghp_[a-zA-Z0-9]{36}'),
        'github_oauth': re.compile(r'gho_[a-zA-Z0-9]{36}'),
        'openai': re.compile(r'sk-[a-zA-Z0-9]{48}'),
        'openai_proj': re.compile(r'sk-proj-[a-zA-Z0-9-_]{80,}'),
        'aws_access': re.compile(r'AKIA[0-9A-Z]{16}'),
        'discord_token': re.compile(r'[MN][A-Za-z0-9]{23,}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27}'),
        'telegram_bot': re.compile(r'[0-9]{8,10}:[A-Za-z0-9_-]{35}'),
        'private_key': re.compile(r'-----BEGIN\s+(RSA|DSA|EC|OPENSSH|PGP)?\s*PRIVATE KEY-----')
    }
    
    def __init__(self):
        self.seen_hashes = set()  # For deduplication
        
    def format_content(self, raw_content: str, source_name: str = "") -> Tuple[str, str]:
        """
        Format content according to specification.
        Returns: (title, formatted_content)
        
        Example output:
        Title: "2x API Keys, 10x Disney+ Login, 42x NordVPN Login"
        
        Content:
        ```
        Title of what was scraped:
        2x API Keys Amazon
        10x Disney+ Login
        42x NordVPN Login
        
        Data that was scraped (at the top should be the actual keys, credentials, keys):
        example@example.com
        example
        
        example2@example.com
        example2
        
        Below that should be the rest of the data scraped:
        Random Data Here That Was Scraped.
        ```
        """
        
        # Extract all credentials
        credentials = self._extract_all_credentials(raw_content)
        
        # Count by type and service
        type_counts = self._count_credentials(credentials)
        
        # Generate title
        title = self._generate_title(type_counts)
        
        # Format the content
        formatted_content = self._format_output(credentials, type_counts, raw_content)
        
        return title, formatted_content
    
    def _extract_all_credentials(self, content: str) -> Dict[str, List[Dict]]:
        """Extract all credentials organized by type"""
        credentials = defaultdict(list)
        
        # Extract email:password combos
        for match in self.PATTERNS['email_pass'].finditer(content):
            email, password = match.groups()
            service = self._detect_service(email, content[max(0, match.start()-100):match.end()+100])
            credentials['email_pass'].append({
                'email': email,
                'password': password,
                'service': service,
                'full': f"{email}:{password}"
            })
        
        # Extract URL:login:pass
        for match in self.PATTERNS['url_login_pass'].finditer(content):
            url, login, password = match.groups()
            service = self._detect_service_from_url(url)
            credentials['url_login_pass'].append({
                'url': url,
                'login': login,
                'password': password,
                'service': service,
                'full': f"{url} | {login} | {password}"
            })
        
        # Extract API keys
        for key_type, pattern in [
            ('GitHub PAT', self.PATTERNS['github_pat']),
            ('GitHub OAuth', self.PATTERNS['github_oauth']),
            ('OpenAI', self.PATTERNS['openai']),
            ('OpenAI Project', self.PATTERNS['openai_proj']),
            ('AWS', self.PATTERNS['aws_access']),
            ('Discord', self.PATTERNS['discord_token']),
            ('Telegram Bot', self.PATTERNS['telegram_bot'])
        ]:
            for match in pattern.finditer(content):
                credentials['api_keys'].append({
                    'type': key_type,
                    'key': match.group(0),
                    'masked': self._mask_key(match.group(0))
                })
        
        # Extract private keys
        if self.PATTERNS['private_key'].search(content):
            key_types = []
            if 'RSA PRIVATE KEY' in content:
                key_types.append('RSA')
            if 'DSA PRIVATE KEY' in content:
                key_types.append('DSA')
            if 'EC PRIVATE KEY' in content:
                key_types.append('EC')
            if 'OPENSSH PRIVATE KEY' in content:
                key_types.append('OpenSSH')
            
            for kt in key_types:
                credentials['private_keys'].append({
                    'type': kt,
                    'preview': f"-----BEGIN {kt} PRIVATE KEY-----"
                })
        
        return credentials
    
    def _detect_service(self, email: str, context: str) -> str:
        """Detect service from email and surrounding context"""
        context_lower = context.lower()
        email_lower = email.lower()
        
        for keyword, service_name in self.SERVICE_NAMES.items():
            if keyword in email_lower or keyword in context_lower:
                return service_name
        
        # Check domain
        if 'gmail' in email_lower:
            return 'Gmail'
        elif 'outlook' in email_lower or 'hotmail' in email_lower:
            return 'Outlook'
        elif 'yahoo' in email_lower:
            return 'Yahoo'
        
        return 'Account'
    
    def _detect_service_from_url(self, url: str) -> str:
        """Detect service from URL"""
        url_lower = url.lower()
        
        for keyword, service_name in self.SERVICE_NAMES.items():
            if keyword in url_lower:
                return service_name
        
        # Extract domain
        import urllib.parse
        try:
            domain = urllib.parse.urlparse(url).netloc
            domain_parts = domain.split('.')
            if len(domain_parts) >= 2:
                site_name = domain_parts[-2]
                return site_name.capitalize()
        except:
            pass
        
        return 'Website'
    
    def _mask_key(self, key: str) -> str:
        """Mask API key for security"""
        if len(key) > 20:
            return key[:8] + "..." + key[-8:]
        elif len(key) > 10:
            return key[:4] + "..." + key[-4:]
        else:
            return key[:2] + "..." + key[-2:]
    
    def _count_credentials(self, credentials: Dict) -> Dict[str, int]:
        """Count credentials by type and service"""
        counts = defaultdict(int)
        
        # Count email/password by service
        service_counts = Counter()
        for cred in credentials.get('email_pass', []):
            service_counts[cred['service']] += 1
        
        for service, count in service_counts.items():
            counts[f"{service} Login"] = count
        
        # Count URL logins
        url_service_counts = Counter()
        for cred in credentials.get('url_login_pass', []):
            url_service_counts[cred['service']] += 1
        
        for service, count in url_service_counts.items():
            counts[f"{service} Login"] = count
        
        # Count API keys
        api_counts = Counter()
        for cred in credentials.get('api_keys', []):
            api_counts[cred['type']] += 1
        
        for api_type, count in api_counts.items():
            counts[f"{api_type}"] = count
        
        # Count private keys
        if credentials.get('private_keys'):
            counts['Private Key'] = len(credentials['private_keys'])
        
        return counts
    
    def _generate_title(self, counts: Dict[str, int]) -> str:
        """Generate title from counts"""
        if not counts:
            return "Credential Leak"
        
        # Sort by count descending, take top 4
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)[:4]
        
        title_parts = []
        for name, count in sorted_counts:
            title_parts.append(f"{count}x {name}")
        
        return ", ".join(title_parts)
    
    def _format_output(self, credentials: Dict, counts: Dict, raw_content: str) -> str:
        """Format the final output according to specification"""
        output = []
        
        # Header section
        output.append("Title of what was scraped:")
        for name, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            output.append(f"{count}x {name}")
        output.append("")
        
        # Credentials section
        output.append("Data that was scraped (at the top should be the actual keys, credentials, keys):")
        
        # Add email:password combos first (most valuable)
        added_creds = set()
        for cred in credentials.get('email_pass', []):
            cred_hash = hashlib.md5(cred['full'].encode()).hexdigest()
            if cred_hash not in added_creds:
                output.append(cred['email'])
                output.append(cred['password'])
                output.append("")
                added_creds.add(cred_hash)
        
        # Add URL logins
        for cred in credentials.get('url_login_pass', [])[:20]:  # Limit to 20
            output.append(f"URL: {cred['url']}")
            output.append(f"Login: {cred['login']}")
            output.append(f"Password: {cred['password']}")
            output.append("")
        
        # Add API keys (masked)
        for cred in credentials.get('api_keys', [])[:20]:  # Limit to 20
            output.append(f"{cred['type']}: {cred['masked']}")
        
        if credentials.get('api_keys'):
            output.append("")
        
        # Add private key indicators
        for cred in credentials.get('private_keys', []):
            output.append(f"{cred['type']} Private Key Found")
        
        if credentials.get('private_keys'):
            output.append("")
        
        # Add separator
        output.append("Below that should be the rest of the data scraped:")
        output.append("-" * 60)
        
        # Add some context from raw content (first 500 chars that aren't already shown)
        context_lines = []
        for line in raw_content.split('\n')[:50]:  # First 50 lines
            line = line.strip()
            if line and not any(line in o for o in output):
                context_lines.append(line)
            if len('\n'.join(context_lines)) > 500:
                break
        
        output.extend(context_lines)
        
        return '\n'.join(output)


def test_formatter():
    """Test the formatter with sample data"""
    formatter = EnhancedCredentialFormatter()
    
    sample_content = """
    Netflix Accounts Fresh 2024
    user1@gmail.com:password123
    user2@yahoo.com:secret456
    
    Disney+ Premium:
    disney@outlook.com:disney789
    
    API Keys:
    ghp_1234567890abcdefghijklmnopqrstuvwxyz1234
    sk-abcdefghijklmnopqrstuvwxyz123456789012345678901
    
    AWS: AKIAIOSFODNN7EXAMPLE
    
    https://example.com admin password123
    """
    
    title, formatted = formatter.format_content(sample_content, "TestSource")
    
    print("TITLE:", title)
    print("\nFORMATTED CONTENT:")
    print(formatted)


if __name__ == "__main__":
    test_formatter()