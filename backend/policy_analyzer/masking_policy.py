import hmac, hashlib, os, ipaddress

MASKING_SECRET = os.environ.get("MASKING_SECRET", "change_this_secret")

def hmac_hash(value: str, length: int = 10) -> str:
    if not value:
        return None
    mac = hmac.new(MASKING_SECRET.encode(), value.encode(), hashlib.sha256).hexdigest()
    return mac[:length]

def mask_ip(ip: str) -> str:
    try:
        addr = ipaddress.ip_address(ip)
        if addr.version == 4:
            parts = str(addr).split(".")
            parts[-1] = "*"
            return ".".join(parts)
        return str(addr).split(":")[0] + ":*"
    except Exception:
        return hmac_hash(ip, 8)

def mask_policy(row: dict) -> dict:
    out = row.copy()
    if "sourceIp" in out:
        out["sourceIp"] = mask_ip(out["sourceIp"])
    if "destinationIp" in out:
        out["destinationIp"] = mask_ip(out["destinationIp"])
    if "accountId" in out:
        out["accountId"] = hmac_hash(out["accountId"])
    return out

def apply_policy_masking(policies: list) -> list:
    return [mask_policy(p) for p in policies]
