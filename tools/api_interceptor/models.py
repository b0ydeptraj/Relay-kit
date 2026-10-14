import json
import re
import time
import uuid
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlparse


KNOWN_TOKEN_KEYS = {
    # TikTok / ByteDance Web & Studio
    "mstoken", "x-bogus", "_signature", "passport-csrf-token", "sessionid",
    "tt_chain_token", "ttreq", "s_v_web_id", "webid", "user_unique_id",
    # TikTok Mobile / Cronet
    "x-gorgon", "x-khronos", "x-argus", "x-ladon", "x-ss-req-ticket",
    "device_id", "install_id", "iid", "openudid", "cdid",
    # Standard & OAuth
    "authorization", "x-csrf-token", "x-xsrf-token", "cookie", "token", "access_token",
    # ASP.NET & Form Credentials
    ".aspxauth", "aspxauth", "__viewstate", "__eventvalidation", "__viewstategenerator",
    "txtusername", "txtpassword", "username", "password", "taikhoan", "matkhau", "log", "pwd",
}


def extract_security_tokens(
    url: str,
    headers: Dict[str, str],
    body: Optional[str] = None
) -> Dict[str, str]:
    """
    Extract security, authentication tokens and credentials from request headers, query string, or body.
    """
    tokens: Dict[str, str] = {}
    lower_headers = {k.lower(): str(v) for k, v in headers.items()}

    # 1. Query parameters
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        for k, v in params.items():
            k_low = k.lower()
            if k_low in KNOWN_TOKEN_KEYS or any(tok in k_low for tok in ("token", "session", "sign", "bogus", "device", "user", "pass")):
                tokens[k] = v[0] if v else ""
    except Exception:
        pass

    # 2. Request Headers
    for k, v in lower_headers.items():
        if k in KNOWN_TOKEN_KEYS:
            tokens[k] = v
        elif any(sig in k for sig in ("x-gorgon", "x-khronos", "x-argus", "x-ladon", "bogus", "signature", "token")):
            tokens[k] = v

    # 3. Cookie Header parse
    cookie_str = lower_headers.get("cookie", "")
    if cookie_str:
        for item in cookie_str.split(";"):
            item = item.strip()
            if "=" in item:
                c_name, c_val = item.split("=", 1)
                c_name_clean = c_name.strip()
                c_name_low = c_name_clean.lower()
                if (
                    c_name_low in KNOWN_TOKEN_KEYS
                    or any(tok in c_name_low for tok in ("auth", "session", "token", "ticket", "jwt", "pass", "user", "uid", "sid"))
                ):
                    tokens[c_name_clean] = c_val.strip()
                    tokens[f"cookie_{c_name_low}"] = c_val.strip()

    # 4. Body inspection (JSON & Form-UrlEncoded)
    if body:
        if body.startswith("{") or body.startswith("["):
            try:
                data = json.loads(body)
                if isinstance(data, dict):
                    for k, v in data.items():
                        k_low = str(k).lower()
                        if k_low in KNOWN_TOKEN_KEYS or any(tok in k_low for tok in ("token", "pass", "user", "auth", "secret")):
                            if isinstance(v, (str, int)):
                                tokens[f"body_{k}"] = str(v)
            except Exception:
                pass
        elif "=" in body:
            try:
                form_params = parse_qs(body)
                for k, v_list in form_params.items():
                    k_low = k.lower()
                    if k_low in KNOWN_TOKEN_KEYS or any(tok in k_low for tok in ("token", "viewstate", "eventvalidation", "user", "pass", "auth", "matkhau", "taikhoan")):
                        val = v_list[0] if v_list else ""
                        tokens[k] = val
            except Exception:
                pass

    return tokens


def classify_request_tags(url: str, method: str = "GET", body: Optional[str] = None) -> list:
    tags = []
    u = url.lower()
    m = method.upper()

    if re.search(r'(auth|login|signin|register|signup|logout|token|session|oauth|passwd|password|taikhoan|matkhau|dangnhap)', u):
        tags.append("AUTH")
    if body and re.search(r'(username|password|pass|user|email|taikhoan|matkhau|dangnhap)', body.lower()):
        if "AUTH" not in tags:
            tags.append("AUTH")
    if re.search(r'(user|profile|account|member|\bme\b|my-)', u):
        tags.append("USER")
    if re.search(r'([?&/](id|uid|user_id|account_id|order_id|item_id|masv|mahv|mssv|studentid|maso|chuyen_nganh|semid|hocky|mamh|mahp)=\d+)', u):
        tags.append("IDOR")
    elif re.search(r'(/[a-z_-]+/\d{2,})', u):
        tags.append("IDOR")
    if re.search(r'(/api/|/v\d+/|graphql|/rpc|/ajax/)', u) or m in ("POST", "PUT", "DELETE", "PATCH"):
        tags.append("API")
    return tags


def is_noise_or_internal(url: str) -> bool:
    u = url.lower()
    if any(h in u for h in ("127.0.0.1:8999", "localhost:8999", ":8998", ":8999", "/api/feed", "/api/request/")):
        return True
    if re.search(r'\.(png|jpe?g|gif|svg|webp|css|woff2?|ttf|eot|ico|map)(\?.*)?$', u):
        return True
    if any(t in u for t in (
        "google-analytics.com", "doubleclick.net", "clarity.ms", "log_event", "telemetry", "collect?",
        "metrics", "facebook.com/tr/", "adtrafficquality.google.com", "play.google.com/log",
        "accounts.google.com/rotatecookies", "validationasyncservice", "async/bgasy"
    )):
        return True
    return False


def inspect_response_importance(
    url: str,
    method: str,
    trigger_action: Optional[str] = None,
    response_body: Optional[str] = None,
) -> tuple:
    """
    Auto-detects if request handles user profile, action execution, or high-value data.
    """
    reasons = []
    summary = ""
    is_important = False

    if trigger_action:
        reasons.append(f'Kích hoạt bởi: "{trigger_action}"')
        is_important = True

    if response_body:
        b_clean = response_body.strip()
        if (b_clean.startswith("{") or b_clean.startswith("[")) and len(b_clean) > 5:
            try:
                data = json.loads(b_clean[:4096])
                data_dict = data if isinstance(data, dict) else (data[0] if isinstance(data, list) and data and isinstance(data[0], dict) else {})
                target_fields = ("username", "user_id", "email", "phone", "profile", "nickname", "account", "balance", "role", "avatar")
                found_keys = []
                for k in target_fields:
                    if k in data_dict or any(k in str(dk).lower() for dk in data_dict.keys()):
                        found_keys.append(k)

                if found_keys:
                    reasons.append(f"Chứa dữ liệu người dùng ({', '.join(found_keys)})")
                    is_important = True
                    summary = json.dumps({k: str(data_dict.get(k))[:30] for k in found_keys[:4] if k in data_dict}, ensure_ascii=False)
            except Exception:
                pass

    if method in ("POST", "PUT", "DELETE", "PATCH") and not any(n in url.lower() for n in ("telemetry", "log_event", "metric")):
        reasons.append(f"Hành động thay đổi dữ liệu ({method})")
        is_important = True

    reason_str = " • ".join(reasons) if reasons else ""
    return is_important, reason_str, summary


class CapturedRequest:
    """Represents a captured HTTP/HTTPS request from Desktop or Mobile."""

    def __init__(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        response_status: int = 200,
        response_headers: Optional[Dict[str, str]] = None,
        response_body: Optional[str] = None,
        source: str = "desktop",
        req_id: Optional[str] = None,
        timestamp: Optional[float] = None,
        tags: Optional[list] = None,
        trigger_action: Optional[str] = None,
        preview_summary: Optional[str] = None,
        is_important: Optional[bool] = None,
    ):
        self.id = req_id or str(uuid.uuid4())[:8]
        self.timestamp = timestamp or time.time()
        self.source = source.lower() if source in ("desktop", "mobile") else "desktop"
        self.url = url
        self.method = method.upper()
        self.headers = headers or {}
        self.body = body or ""
        self.response_status = response_status
        self.response_headers = response_headers or {}
        self.response_body = response_body or ""
        self.trigger_action = trigger_action

        parsed = urlparse(self.url)
        self.host = parsed.netloc
        self.path = parsed.path or "/"

        # Auto-extract security tokens & classification tags
        self.extracted_tokens = extract_security_tokens(self.url, self.headers, self.body)
        self.tags = tags or classify_request_tags(self.url, self.method, self.body)
        self.is_noise = is_noise_or_internal(self.url)

        # Smart Action-Correlation & Auto-Spotlight
        detected_imp, detected_reason, detected_summary = inspect_response_importance(
            self.url, self.method, self.trigger_action, self.response_body
        )
        self.is_important = is_important if is_important is not None else detected_imp
        self.highlight_reason = detected_reason
        self.preview_summary = preview_summary or detected_summary

        if self.trigger_action and "ACTION" not in self.tags:
            self.tags.append("ACTION")

        if self.is_important and "IMPORTANT" not in self.tags:
            self.tags.insert(0, "IMPORTANT")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "source": self.source,
            "method": self.method,
            "url": self.url,
            "host": self.host,
            "path": self.path,
            "headers": self.headers,
            "body": self.body,
            "response_status": self.response_status,
            "response_headers": self.response_headers,
            "response_body": self.response_body[:2048] if self.response_body else "",
            "extracted_tokens": self.extracted_tokens,
            "tags": self.tags,
            "is_noise": self.is_noise,
            "trigger_action": self.trigger_action,
            "is_important": self.is_important,
            "highlight_reason": self.highlight_reason,
            "preview_summary": self.preview_summary,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CapturedRequest":
        return cls(
            url=data.get("url", ""),
            method=data.get("method", "GET"),
            headers=data.get("headers"),
            body=data.get("body"),
            response_status=data.get("response_status", 200),
            response_headers=data.get("response_headers"),
            response_body=data.get("response_body"),
            source=data.get("source", "desktop"),
            req_id=data.get("id"),
            timestamp=data.get("timestamp"),
            tags=data.get("tags"),
            trigger_action=data.get("trigger_action"),
            preview_summary=data.get("preview_summary"),
            is_important=data.get("is_important"),
        )


# IDOR param name patterns (numeric/sequential IDs worth fuzzing)
import re as _re
_IDOR_PARAM_RE = _re.compile(
    r'^(id|uid|user_?id|account_?id|student_?id|masv|mahv|mssv|maso|ma_?sv|mahs|'
    r'chuyen_?nganh|nganh|semid|hoc_?ky|hocky|mamh|mahp|order_?id|item_?id|doc_?id|'
    r'file_?id|record_?id|pid|sid|tid|gid|ref|num|idx|index)$',
    _re.IGNORECASE
)


def detect_idor_params(url, body=None):
    from urllib.parse import parse_qs, urlparse
    candidates = {}
    try:
        parsed = urlparse(url)
        for k, vlist in parse_qs(parsed.query).items():
            v = vlist[0] if vlist else ''
            if _IDOR_PARAM_RE.match(k) or (v.isdigit() and 0 < len(v) <= 12 and int(v) > 0):
                candidates[k] = v
    except Exception:
        pass
    if body and '=' in body:
        try:
            for k, vlist in parse_qs(body).items():
                v = vlist[0] if vlist else ''
                if _IDOR_PARAM_RE.match(k) or (v.isdigit() and 0 < len(v) <= 12 and int(v) > 0):
                    if k.upper() not in ('__VIEWSTATE', '__EVENTVALIDATION', '__VIEWSTATEGENERATOR'):
                        candidates[k] = v
        except Exception:
            pass
    return candidates
