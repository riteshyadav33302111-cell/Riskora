"""
Riskora – Revised Feature Extraction Module
=============================================
Uses the original PhiUSIIL dataset's URL-only features DIRECTLY, 
ensuring consistent feature semantics between training and inference.

Key insight from EDA:
  - The PhiUSIIL dataset labels are based on browser/content inspection
  - Many seemingly-clean URLs are phishing (they use HTTPS, short domains)
  - Only URL-string features that DO NOT require fetching the page are used
  - Custom heuristics supplement dataset features for inference on new URLs

FEATURE DESIGN PHILOSOPHY:
  We use the ORIGINAL dataset column names and definitions wherever possible,
  then replicate those computations during inference from the URL string.

Dataset: PhiUSIIL Phishing URL Dataset
Source : https://archive.ics.uci.edu/dataset/967/phiusiil+phishing+url+dataset
Licence: Creative Commons Attribution 4.0 International (CC BY 4.0)
"""

from __future__ import annotations

import re
import math
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Any


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SUSPICIOUS_KEYWORDS: List[str] = [
    "login", "signin", "verify", "account", "secure", "update",
    "banking", "confirm", "password", "credential", "wallet",
    "paypal", "ebay", "amazon", "apple", "google", "microsoft",
    "support", "alert", "suspended", "limited", "unusual",
    "phishing", "click", "free", "win", "prize", "lucky",
    "urgent", "immediately", "access", "authenticate",
]

SUSPICIOUS_TLDS: List[str] = [
    "tk", "ml", "ga", "cf", "gq", "xyz", "top", "club",
    "online", "site", "website", "space", "press",
]

# ---------------------------------------------------------------------------
# Feature definitions (mapping to original PhiUSIIL column semantics)
# ---------------------------------------------------------------------------

def _url_length(url: str) -> int:
    """URLLength: total length of URL string."""
    return len(url)


def _domain_length(domain: str) -> int:
    """DomainLength: length of the hostname."""
    return len(domain)


def _is_domain_ip(domain: str) -> int:
    """IsDomainIP: 1 if domain is a raw IP address."""
    ipv4 = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
    ipv6 = re.compile(r'^\[?[0-9a-fA-F:]+\]?$')
    return int(bool(ipv4.match(domain) or ipv6.match(domain)))


def _tld_length(url: str) -> int:
    """TLDLength: length of the TLD."""
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    parts = hostname.split(".")
    return len(parts[-1]) if len(parts) >= 2 else 0


def _no_of_subdomains(hostname: str) -> int:
    """NoOfSubDomain: number of subdomain levels."""
    parts = hostname.split(".")
    return max(0, len(parts) - 2)


def _has_obfuscation(url: str) -> int:
    """HasObfuscation: 1 if URL contains percent-encoded chars."""
    return int(bool(re.search(r'%[0-9a-fA-F]{2}', url)))


def _no_of_letters(url: str) -> int:
    """NoOfLettersInURL: count of alphabetic chars."""
    return sum(c.isalpha() for c in url)


def _letter_ratio(url: str) -> float:
    """LetterRatioInURL: ratio of alphabetic chars to URL length."""
    return sum(c.isalpha() for c in url) / max(1, len(url))


def _no_of_digits(url: str) -> int:
    """NoOfDegitsInURL: count of digit chars."""
    return sum(c.isdigit() for c in url)


def _digit_ratio(url: str) -> float:
    """DegitRatioInURL: ratio of digit chars to URL length."""
    return sum(c.isdigit() for c in url) / max(1, len(url))


def _no_of_equals(url: str) -> int:
    """NoOfEqualsInURL: count of '=' chars."""
    return url.count('=')


def _no_of_qmarks(url: str) -> int:
    """NoOfQMarkInURL: count of '?' chars."""
    return url.count('?')


def _no_of_ampersands(url: str) -> int:
    """NoOfAmpersandInURL: count of '&' chars."""
    return url.count('&')


def _no_of_other_special(url: str) -> int:
    """NoOfOtherSpecialCharsInURL: special chars excluding common ones."""
    normal = set("abcdefghijklmnopqrstuvwxyz"
                 "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                 "0123456789/.-_:?=&@%")
    return sum(1 for c in url if c not in normal)


def _special_char_ratio(url: str) -> float:
    """SpacialCharRatioInURL: ratio of special chars to URL length."""
    normal = set("abcdefghijklmnopqrstuvwxyz"
                 "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                 "0123456789/.-_")
    special = sum(1 for c in url if c not in normal)
    return special / max(1, len(url))


def _is_https(url: str) -> int:
    """IsHTTPS: 1 if URL uses HTTPS."""
    return 1 if url.lower().startswith("https://") else 0


# ---------------------------------------------------------------------------
# Additional heuristics (supplement original features)
# ---------------------------------------------------------------------------

def _url_entropy(url: str) -> float:
    """Shannon entropy of the URL string."""
    if not url:
        return 0.0
    freq: Dict[str, int] = {}
    for ch in url:
        freq[ch] = freq.get(ch, 0) + 1
    n = len(url)
    return -sum((c / n) * math.log2(c / n) for c in freq.values())


def _has_suspicious_tld(url: str) -> int:
    """1 if TLD is in the high-abuse list."""
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    parts = hostname.split(".")
    tld = parts[-1].lower() if parts else ""
    return int(tld in SUSPICIOUS_TLDS)


def _has_at_symbol(url: str) -> int:
    """1 if URL contains '@' (redirection deception)."""
    return int('@' in url)


def _has_port(url: str) -> int:
    """1 if an explicit port is in the URL."""
    parsed = urlparse(url)
    return int(parsed.port is not None)


def _url_path_depth(url: str) -> int:
    """Number of non-empty path segments."""
    parsed = urlparse(url)
    return len([s for s in parsed.path.split('/') if s])


def _domain_hyphen_count(domain: str) -> int:
    """Number of hyphens in the domain."""
    return domain.count('-')


def _suspicious_keyword_count(url: str) -> int:
    """Count of distinct suspicious keywords in the URL."""
    url_lower = url.lower()
    return sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in url_lower)


def _no_of_dots(url: str) -> int:
    """Total dots in the URL."""
    return url.count('.')


def _no_of_hyphens(url: str) -> int:
    """Total hyphens in the URL."""
    return url.count('-')


def _query_param_count(url: str) -> int:
    """Number of query parameters."""
    parsed = urlparse(url)
    return len(parse_qs(parsed.query))


def _domain_has_numbers(domain: str) -> int:
    """1 if the domain contains digits."""
    bare = re.sub(r'^www\.', '', domain, flags=re.IGNORECASE)
    return int(bool(re.search(r'\d', bare)))


# ---------------------------------------------------------------------------
# FEATURE_NAMES and extract_features
# ---------------------------------------------------------------------------

FEATURE_NAMES: List[str] = [
    # Original PhiUSIIL URL-only columns (replicated)
    "URLLength",
    "DomainLength",
    "IsDomainIP",
    "TLDLength",
    "NoOfSubDomain",
    "HasObfuscation",
    "NoOfLettersInURL",
    "LetterRatioInURL",
    "NoOfDegitsInURL",
    "DegitRatioInURL",
    "NoOfEqualsInURL",
    "NoOfQMarkInURL",
    "NoOfAmpersandInURL",
    "NoOfOtherSpecialCharsInURL",
    "SpacialCharRatioInURL",
    "IsHTTPS",
    # Supplementary heuristics
    "url_entropy",
    "has_suspicious_tld",
    "has_at_symbol",
    "has_port",
    "url_path_depth",
    "domain_hyphen_count",
    "suspicious_keyword_count",
    "no_of_dots",
    "no_of_hyphens",
    "query_param_count",
    "domain_has_numbers",
]


def extract_features(url: str) -> Dict[str, Any]:
    """
    Extract all Riskora features from a URL string.
    
    Uses the same column definitions as PhiUSIIL dataset's URL-only features,
    ensuring consistent semantics between training and inference.
    """
    url = url.strip()
    parsed = urlparse(url)
    domain = parsed.hostname or ""
    bare_domain = re.sub(r'^www\.', '', domain, flags=re.IGNORECASE)

    return {
        # Original dataset features
        "URLLength":                 _url_length(url),
        "DomainLength":              _domain_length(domain),
        "IsDomainIP":                _is_domain_ip(domain),
        "TLDLength":                 _tld_length(url),
        "NoOfSubDomain":             _no_of_subdomains(domain),
        "HasObfuscation":            _has_obfuscation(url),
        "NoOfLettersInURL":          _no_of_letters(url),
        "LetterRatioInURL":          round(_letter_ratio(url), 6),
        "NoOfDegitsInURL":           _no_of_digits(url),
        "DegitRatioInURL":           round(_digit_ratio(url), 6),
        "NoOfEqualsInURL":           _no_of_equals(url),
        "NoOfQMarkInURL":            _no_of_qmarks(url),
        "NoOfAmpersandInURL":        _no_of_ampersands(url),
        "NoOfOtherSpecialCharsInURL":_no_of_other_special(url),
        "SpacialCharRatioInURL":     round(_special_char_ratio(url), 6),
        "IsHTTPS":                   _is_https(url),
        # Supplementary heuristics
        "url_entropy":               round(_url_entropy(url), 6),
        "has_suspicious_tld":        _has_suspicious_tld(url),
        "has_at_symbol":             _has_at_symbol(url),
        "has_port":                  _has_port(url),
        "url_path_depth":            _url_path_depth(url),
        "domain_hyphen_count":       _domain_hyphen_count(bare_domain),
        "suspicious_keyword_count":  _suspicious_keyword_count(url),
        "no_of_dots":                _no_of_dots(url),
        "no_of_hyphens":             _no_of_hyphens(url),
        "query_param_count":         _query_param_count(url),
        "domain_has_numbers":        _domain_has_numbers(domain),
    }


def extract_feature_vector(url: str) -> List[float]:
    """Return flat list in FEATURE_NAMES order for scikit-learn."""
    feat_dict = extract_features(url)
    return [feat_dict[name] for name in FEATURE_NAMES]


# Human-readable descriptions for the API
FEATURE_DESCRIPTIONS: Dict[str, str] = {
    "URLLength":                  "Total length of the URL string",
    "DomainLength":               "Length of the domain / hostname",
    "IsDomainIP":                 "Whether the domain is a raw IP address",
    "TLDLength":                  "Length of the top-level domain",
    "NoOfSubDomain":              "Number of subdomain levels",
    "HasObfuscation":             "Whether percent-encoded characters are present",
    "NoOfLettersInURL":           "Count of alphabetic characters in URL",
    "LetterRatioInURL":           "Ratio of alphabetic chars to URL length",
    "NoOfDegitsInURL":            "Count of digit characters in URL",
    "DegitRatioInURL":            "Ratio of digits to URL length",
    "NoOfEqualsInURL":            "Count of '=' characters (query params)",
    "NoOfQMarkInURL":             "Count of '?' characters",
    "NoOfAmpersandInURL":         "Count of '&' characters",
    "NoOfOtherSpecialCharsInURL": "Count of unusual special characters",
    "SpacialCharRatioInURL":      "Ratio of special chars to URL length",
    "IsHTTPS":                    "Whether the URL uses HTTPS",
    "url_entropy":                "Shannon entropy (randomness measure)",
    "has_suspicious_tld":         "Whether TLD is in the high-abuse list",
    "has_at_symbol":              "'@' in URL can mislead users about destination",
    "has_port":                   "Explicit non-standard port in URL",
    "url_path_depth":             "Number of path segments after domain",
    "domain_hyphen_count":        "Number of hyphens in domain segment",
    "suspicious_keyword_count":   "Count of phishing-related keywords",
    "no_of_dots":                 "Total dot count in URL",
    "no_of_hyphens":              "Total hyphen count in URL",
    "query_param_count":          "Number of query parameters",
    "domain_has_numbers":         "Whether domain contains numeric characters",
}


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    test_urls = [
        "https://www.google.com",
        "http://192.168.1.1/login.php",
        "https://paypal-verify.tk/account?token=abc123",
        "https://www.amazon.com/dp/B08N5WRWNW?ref=sr&tag=abc",
    ]
    for url in test_urls:
        feats = extract_features(url)
        print(f"\nURL: {url}")
        for k, v in feats.items():
            print(f"  {k:35s}: {v}")
