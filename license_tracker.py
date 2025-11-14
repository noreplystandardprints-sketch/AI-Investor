"""
Commercial License Tracking System for AI-Investor

Manages commercial license issuance, storage, and verification.
License data stored in JSON with hashed passwords for security.
"""

import json
import os
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple

LICENSE_DATABASE = "licenses/commercial_licenses.json"
LICENSE_DIR = "licenses"


def _ensure_license_dir():
    """Ensure licenses directory exists."""
    os.makedirs(LICENSE_DIR, exist_ok=True)


def _hash_password(password: str, salt: str = None) -> Tuple[str, str]:
    """Hash a password with salt using SHA-256. Returns (hash, salt)."""
    if salt is None:
        salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((password + salt).encode())
    return hash_obj.hexdigest(), salt


def _load_licenses() -> Dict:
    """Load commercial licenses from JSON file."""
    _ensure_license_dir()
    if os.path.exists(LICENSE_DATABASE):
        try:
            with open(LICENSE_DATABASE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load licenses: {e}")
            return {"licenses": {}, "metadata": {}}
    return {"licenses": {}, "metadata": {}}


def _save_licenses(data: Dict):
    """Save commercial licenses to JSON file."""
    _ensure_license_dir()
    try:
        with open(LICENSE_DATABASE, 'w') as f:
            json.dump(data, f, indent=2)
        os.chmod(LICENSE_DATABASE, 0o600)  # Restrict to owner only
    except Exception as e:
        print(f"Error saving licenses: {e}")


def issue_license(
    company_name: str,
    contact_email: str,
    commercial_use_case: str,
    expiration_days: int = 365,
    max_instances: int = 1
) -> Tuple[str, str]:
    """
    Issue a new commercial license.
    
    Returns: (license_id, password)
    
    Args:
        company_name: Name of company/individual
        contact_email: Contact email for support
        commercial_use_case: Description of intended commercial use
        expiration_days: Days until license expires (default 365)
        max_instances: Maximum number of instances allowed
    """
    _ensure_license_dir()
    
    # Generate unique license ID and password
    license_id = f"AI-INV-{uuid.uuid4().hex[:12].upper()}"
    password = secrets.token_urlsafe(16)
    password_hash, salt = _hash_password(password)
    
    # Create license record
    license_data = {
        "license_id": license_id,
        "company_name": company_name,
        "contact_email": contact_email,
        "commercial_use_case": commercial_use_case,
        "issued_date": datetime.now().isoformat(),
        "expiration_date": (datetime.now() + timedelta(days=expiration_days)).isoformat(),
        "status": "active",
        "max_instances": max_instances,
        "password_hash": password_hash,
        "salt": salt,
        "activations": 0,
    }
    
    # Save to database
    data = _load_licenses()
    data["licenses"][license_id] = license_data
    data["metadata"]["last_updated"] = datetime.now().isoformat()
    _save_licenses(data)
    
    print(f"✅ License issued: {license_id}")
    print(f"Company: {company_name}")
    print(f"Expiration: {license_data['expiration_date']}")
    
    return license_id, password


def verify_license(license_id: str, password: str) -> Tuple[bool, Optional[Dict]]:
    """
    Verify a commercial license with ID and password.
    
    Returns: (is_valid, license_record)
    """
    data = _load_licenses()
    
    if license_id not in data.get("licenses", {}):
        return False, None
    
    license_record = data["licenses"][license_id]
    
    # Check if expired
    expiration = datetime.fromisoformat(license_record["expiration_date"])
    if datetime.now() > expiration:
        return False, license_record
    
    # Check if active
    if license_record.get("status") != "active":
        return False, license_record
    
    # Verify password
    provided_hash, _ = _hash_password(password, license_record["salt"])
    if provided_hash != license_record["password_hash"]:
        return False, license_record
    
    return True, license_record


def activate_license(license_id: str, password: str, instance_identifier: str = None) -> Tuple[bool, str]:
    """
    Activate/authenticate a commercial license instance.
    
    Returns: (success, message)
    """
    is_valid, license_record = verify_license(license_id, password)
    
    if not is_valid:
        if license_record is None:
            return False, "License ID not found"
        expiration = datetime.fromisoformat(license_record["expiration_date"])
        if datetime.now() > expiration:
            return False, "License has expired"
        if license_record.get("status") != "active":
            return False, f"License is {license_record.get('status', 'unknown')}"
        return False, "Invalid password"
    
    # Check activation limit
    max_instances = license_record.get("max_instances", 1)
    current_activations = license_record.get("activations", 0)
    
    if current_activations >= max_instances:
        return False, f"License activation limit ({max_instances}) exceeded"
    
    # Increment activation count
    data = _load_licenses()
    data["licenses"][license_id]["activations"] = current_activations + 1
    data["licenses"][license_id]["last_activation"] = datetime.now().isoformat()
    if instance_identifier:
        data["licenses"][license_id]["last_instance"] = instance_identifier
    _save_licenses(data)
    
    company = license_record["company_name"]
    return True, f"License activated for {company}"


def list_licenses(show_passwords: bool = False) -> str:
    """
    List all commercial licenses (admin view).
    
    Args:
        show_passwords: If True, show password hashes (DANGEROUS - for admin review only)
    """
    data = _load_licenses()
    licenses = data.get("licenses", {})
    
    if not licenses:
        return "No commercial licenses issued yet."
    
    output = f"\n{'='*80}\nCommercial Licenses ({len(licenses)} total)\n{'='*80}\n"
    
    for license_id, record in licenses.items():
        status = record.get("status", "unknown")
        company = record["company_name"]
        email = record.get("contact_email", "N/A")
        expiration = record.get("expiration_date", "N/A")
        activations = record.get("activations", 0)
        max_inst = record.get("max_instances", 1)
        
        # Check if expired
        try:
            exp_date = datetime.fromisoformat(expiration)
            if datetime.now() > exp_date:
                status = "EXPIRED"
        except:
            pass
        
        output += f"\nLicense ID: {license_id}\n"
        output += f"  Company: {company}\n"
        output += f"  Email: {email}\n"
        output += f"  Status: {status}\n"
        output += f"  Expires: {expiration}\n"
        output += f"  Activations: {activations}/{max_inst}\n"
        
        if show_passwords:
            output += f"  Password Hash: {record.get('password_hash', 'N/A')[:16]}...\n"
    
    output += f"\n{'='*80}\n"
    return output


def revoke_license(license_id: str) -> bool:
    """Revoke a commercial license."""
    data = _load_licenses()
    
    if license_id not in data.get("licenses", {}):
        print(f"License {license_id} not found")
        return False
    
    data["licenses"][license_id]["status"] = "revoked"
    data["licenses"][license_id]["revoked_date"] = datetime.now().isoformat()
    _save_licenses(data)
    
    print(f"✅ License {license_id} revoked")
    return True


def get_license_status(license_id: str, password: str) -> str:
    """Get human-readable status of a license."""
    is_valid, record = verify_license(license_id, password)
    
    if record is None:
        return "License ID not found"
    
    if not is_valid:
        status = record.get("status", "unknown")
        if status == "revoked":
            return "License has been revoked"
        expiration = datetime.fromisoformat(record.get("expiration_date", ""))
        if datetime.now() > expiration:
            return f"License expired on {record['expiration_date']}"
        return "Invalid password or inactive license"
    
    company = record["company_name"]
    exp = record["expiration_date"]
    activations = record.get("activations", 0)
    max_inst = record.get("max_instances", 1)
    
    return f"✅ Valid license for {company}\nExpires: {exp}\nActivations: {activations}/{max_inst}"
