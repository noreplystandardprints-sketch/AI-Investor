"""
Commercial License Tracking System for AI-Investor

Manages commercial license issuance, storage, and verification.
License data stored in JSON with hashed passwords for security.

Admin Authentication:
- Only admin users can issue, revoke, or list licenses
- Admin credentials stored separately in admin_credentials.json
- All admin actions are logged
"""

import json
import os
import hashlib
import secrets
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from enum import Enum
import pandas as pd

class LicenseType(Enum):
    COMMERCIAL = "commercial"
    REGULAR = "regular"

class LicenseStatus(Enum):
    VALID = "valid"
    INVALID = "invalid"
    EXPIRED = "expired"
    NOT_FOUND = "not_found"
    REVOKED = "revoked"

REGULAR_LICENSE_DATABASE = "licenses/regular_licenses.json"
LICENSE_DATABASE = "licenses/commercial_licenses.json"
ADMIN_CREDENTIALS = "licenses/admin_credentials.json"
ADMIN_LOG = "licenses/admin_actions.log"
LICENSE_DIR = "licenses"

# Setup logging
logging.basicConfig(
    filename=ADMIN_LOG,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def _ensure_license_dir():
    """Ensure licenses directory exists."""
    os.makedirs(LICENSE_DIR, exist_ok=True)


def _setup_admin() -> Tuple[str, str]:
    """
    Initialize admin credentials (one-time setup).
    Returns: (admin_username, admin_password)
    """
    _ensure_license_dir()
    
    if os.path.exists(ADMIN_CREDENTIALS):
        print("Admin already initialized")
        return None, None
    
    admin_user = input("Set admin username: ").strip()
    admin_pass = input("Set admin password (will be hashed): ").strip()
    
    if not admin_user or not admin_pass:
        print("Admin username and password required")
        return None, None
    
    admin_hash, admin_salt = _hash_password(admin_pass)
    
    admin_data = {
        "username": admin_user,
        "password_hash": admin_hash,
        "salt": admin_salt,
        "created": datetime.now().isoformat()
    }
    
    with open(ADMIN_CREDENTIALS, 'w') as f:
        json.dump(admin_data, f, indent=2)
    os.chmod(ADMIN_CREDENTIALS, 0o600)
    
    logging.info(f"Admin initialized: {admin_user}")
    print(f"✅ Admin credentials saved securely")
    return admin_user, admin_pass


def _verify_admin(username: str, password: str) -> bool:
    """
    Verify admin credentials.
    """
    if not os.path.exists(ADMIN_CREDENTIALS):
        print("❌ Admin not initialized. Run --license-action admin-init first")
        return False
    
    try:
        with open(ADMIN_CREDENTIALS, 'r') as f:
            admin_data = json.load(f)
        
        if admin_data.get("username") != username:
            logging.warning(f"Failed admin login attempt: wrong username {username}")
            return False
        
        provided_hash, _ = _hash_password(password, admin_data["salt"])
        if provided_hash != admin_data["password_hash"]:
            logging.warning(f"Failed admin login attempt: wrong password for {username}")
            return False
        
        logging.info(f"Admin authenticated: {username}")
        return True
    except Exception as e:
        logging.error(f"Admin verification error: {e}")
        print(f"Error verifying admin: {e}")
        return False


def _hash_password(password: str, salt: str = None) -> Tuple[str, str]:
    """Hash a password with salt using SHA-256. Returns (hash, salt)."""
    if salt is None:
        salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((password + salt).encode())
    return hash_obj.hexdigest(), salt


def _load_regular_licenses() -> Dict:
    """Load regular licenses from JSON file."""
    _ensure_license_dir()
    if os.path.exists(REGULAR_LICENSE_DATABASE):
        try:
            with open(REGULAR_LICENSE_DATABASE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load regular licenses: {e}")
            return {"licenses": {}}
    return {"licenses": {}}


def _save_regular_licenses(data: Dict):
    """Save regular licenses to JSON file."""
    _ensure_license_dir()
    try:
        with open(REGULAR_LICENSE_DATABASE, 'w') as f:
            json.dump(data, f, indent=2)
        os.chmod(REGULAR_LICENSE_DATABASE, 0o600)  # Restrict to owner only
    except Exception as e:
        print(f"Error saving regular licenses: {e}")


def issue_regular_license(
    expiration_days: int = 30,
    admin_username: str = None,
    admin_password: str = None
) -> Tuple[Optional[str], str]:
    """
    Issue a new regular license (ADMIN ONLY).
    
    Returns: (license_code, message)
    """
    try:
        # Verify admin
        if not admin_username or not admin_password:
            return None, "❌ Admin credentials required"
        
        if not _verify_admin(admin_username, admin_password):
            return None, "❌ Admin authentication failed"
        
        _ensure_license_dir()
        
        # Generate unique license code
        license_code = f"REG-{uuid.uuid4().hex[:12].upper()}"
        
        # Create license record
        license_data = {
            "license_code": license_code,
            "issued_date": datetime.now().isoformat(),
            "expiration_date": (datetime.now() + timedelta(days=expiration_days)).isoformat(),
            "status": "active",
            "license_type": LicenseType.REGULAR.value,
        }
        
        # Save to database
        data = _load_regular_licenses()
        data["licenses"][license_code] = license_data
        _save_regular_licenses(data)
        
        msg = f"✅ Regular license issued: {license_code}"
        logging.info(f"Regular license issued by {admin_username}: {license_code}")
        
        return license_code, msg
    except Exception as e:
        error_msg = f"❌ Error issuing regular license: {str(e)}"
        logging.error(error_msg)
        return None, error_msg


def verify_regular_license(license_code: str) -> Tuple[LicenseStatus, Optional[Dict]]:
    """
    Verify a regular license code.
    
    Returns: (LicenseStatus, license_record)
    """
    data = _load_regular_licenses()
    
    if license_code not in data.get("licenses", {}):
        return LicenseStatus.NOT_FOUND, None
    
    license_record = data["licenses"][license_code]
    
    # Check if expired
    expiration = datetime.fromisoformat(license_record["expiration_date"])
    if datetime.now() > expiration:
        return LicenseStatus.EXPIRED, license_record
    
    # Check if active
    if license_record.get("status") != "active":
        return LicenseStatus.INVALID, license_record
    
    return LicenseStatus.VALID, license_record


def revoke_regular_license(license_code: str, admin_username: str = None, admin_password: str = None) -> Tuple[bool, str]:
    """
    Revoke a regular license (ADMIN ONLY).
    """
    try:
        # Verify admin
        if not admin_username or not admin_password:
            return False, "❌ Admin credentials required"
        
        if not _verify_admin(admin_username, admin_password):
            return False, "❌ Admin authentication failed"
        
        data = _load_regular_licenses()
        
        if license_code not in data.get("licenses", {}):
            return False, f"❌ License {license_code} not found"
        
        data["licenses"][license_code]["status"] = "revoked"
        data["licenses"][license_code]["revoked_date"] = datetime.now().isoformat()
        _save_regular_licenses(data)
        
        msg = f"✅ Regular license {license_code} revoked"
        logging.info(f"Regular license revoked by {admin_username}: {license_code}")
        
        return True, msg
    except Exception as e:
        error_msg = f"❌ Error revoking regular license: {str(e)}"
        logging.error(error_msg)
        return False, error_msg


def list_regular_licenses() -> str:
    """
    List all regular licenses (admin view).
    """
    data = _load_regular_licenses()
    licenses = data.get("licenses", {})
    
    if not licenses:
        return "No regular licenses issued yet."
    
    output = f"\n{'='*80}\nRegular Licenses ({len(licenses)} total)\n{'='*80}\n"
    
    for license_code, record in licenses.items():
        status = record.get("status", "unknown")
        expiration = record.get("expiration_date", "N/A")
        
        # Check if expired
        try:
            exp_date = datetime.fromisoformat(expiration)
            if datetime.now() > exp_date:
                status = "EXPIRED"
        except:
            pass
        
        output += f"\nLicense Code: {license_code}\n"
        output += f"  Status: {status}\n"
        output += f"  Expires: {expiration}\n"
        output += f"  Type: {record.get("license_type", "regular").capitalize()}\n"
    
    output += f"\n{'='*80}\n"
    return output


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
    max_instances: int = 1,
    admin_username: str = None,
    admin_password: str = None,
    license_type: LicenseType = LicenseType.COMMERCIAL
) -> Tuple[Optional[str], Optional[str], str]:
    """
    Issue a new commercial license (ADMIN ONLY).
    
    Returns: (license_id, password, message)
    
    Args:
        company_name: Name of company/individual
        contact_email: Contact email for support
        commercial_use_case: Description of intended commercial use
        expiration_days: Days until license expires (default 365)
        max_instances: Maximum number of instances allowed
        admin_username: Admin username for authentication
        admin_password: Admin password for authentication
    """
    try:
        # Verify admin
        if not admin_username or not admin_password:
            return None, None, "❌ Admin credentials required"
        
        if not _verify_admin(admin_username, admin_password):
            return None, None, "❌ Admin authentication failed"
        
        # Validate inputs
        if not all([company_name, contact_email, commercial_use_case]):
            return None, None, "❌ company_name, contact_email, and use_case are required"
        
        if expiration_days < 1 or max_instances < 1:
            return None, None, "❌ expiration_days and max_instances must be >= 1"
        
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
            "license_type": license_type.value,
        }
        
        # Save to database
        data = _load_licenses()
        data["licenses"][license_id] = license_data
        data["metadata"]["last_updated"] = datetime.now().isoformat()
        _save_licenses(data)
        
        msg = f"✅ License issued: {license_id}"
        logging.info(f"License issued by {admin_username}: {license_id} for {company_name}")
        
        return license_id, password, msg
    except Exception as e:
        error_msg = f"❌ Error issuing license: {str(e)}"
        logging.error(error_msg)
        return None, None, error_msg

def generate_commercial_licenses(
    num_licenses: int,
    admin_username: str,
    admin_password: str,
    base_company_name: str = "AI-Investor Commercial User",
    base_contact_email: str = "commercial@ai-investor.com",
    base_use_case: str = "Algorithmic Trading and Market Analysis",
    expiration_days: int = 365,
    max_instances: int = 1,
    output_excel_filename: str = "commercial_licenses.xlsx"
) -> Tuple[bool, str]:
    """
    Generates multiple commercial licenses and exports them to an Excel file.
    """
    try:
        if not _verify_admin(admin_username, admin_password):
            return False, "❌ Admin authentication failed"

        licenses_data = []
        for i in range(num_licenses):
            company_name = f"{base_company_name} {i+1}"
            contact_email = f"user{i+1}_{base_contact_email}"
            
            license_id, password, msg = issue_license(
                company_name=company_name,
                contact_email=contact_email,
                commercial_use_case=base_use_case,
                expiration_days=expiration_days,
                max_instances=max_instances,
                admin_username=admin_username,
                admin_password=admin_password
            )
            
            if license_id:
                licenses_data.append({
                    "License ID": license_id,
                    "Password": password,
                    "Company Name": company_name,
                    "Contact Email": contact_email,
                    "Use Case": base_use_case,
                    "Issued Date": datetime.now().isoformat(),
                    "Expiration Date": (datetime.now() + timedelta(days=expiration_days)).isoformat(),
                    "Max Instances": max_instances,
                    "Status": "active"
                })
            else:
                logging.error(f"Failed to generate license {i+1}: {msg}")
                return False, f"❌ Failed to generate license {i+1}: {msg}"
        
        success, export_msg = export_licenses_to_excel(licenses_data, output_excel_filename)
        if not success:
            return False, f"❌ Generated licenses but failed to export to Excel: {export_msg}"

        return True, f"✅ Successfully generated {num_licenses} commercial licenses and exported to {output_excel_filename}"

    except Exception as e:
        error_msg = f"❌ Error generating commercial licenses: {str(e)}"
        logging.error(error_msg)
        return False, error_msg


def verify_license(license_id: str, password: str = None) -> Tuple[LicenseStatus, Optional[LicenseType], Optional[Dict]]:
    """
    Verify a commercial license with ID and password.
    
    Returns: (LicenseStatus, LicenseType, license_record)
    """
    data = _load_licenses()
    
    if license_id not in data.get("licenses", {}):
        return LicenseStatus.NOT_FOUND, None, None
    
    license_record = data["licenses"][license_id]
    
    # Check if expired
    expiration = datetime.fromisoformat(license_record["expiration_date"])
    if datetime.now() > expiration:
        return LicenseStatus.EXPIRED, LicenseType(license_record["license_type"]), license_record
    
    # Check if active
    if license_record.get("status") != "active":
        return LicenseStatus.INVALID, LicenseType(license_record["license_type"]), license_record
    
    # Verify password only if provided and license type is commercial
    if password and license_record.get("license_type") == LicenseType.COMMERCIAL.value:
        provided_hash, _ = _hash_password(password, license_record["salt"])
        if provided_hash != license_record["password_hash"]:
            return LicenseStatus.INVALID, LicenseType(license_record["license_type"]), license_record
    
    return LicenseStatus.VALID, LicenseType(license_record["license_type"]), license_record


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
        output += f"  Type: {record.get("license_type", "commercial").capitalize()}\n"
        
        if show_passwords:
            output += f"  Password Hash: {record.get('password_hash', 'N/A')[:16]}...\n"
    
    output += f"\n{'='*80}\n"
    return output


def revoke_license(license_id: str, admin_username: str = None, admin_password: str = None) -> Tuple[bool, str]:
    """
    Revoke a commercial license (ADMIN ONLY).
    """
    try:
        # Verify admin
        if not admin_username or not admin_password:
            return False, "❌ Admin credentials required"
        
        if not _verify_admin(admin_username, admin_password):
            return False, "❌ Admin authentication failed"
        
        data = _load_licenses()
        
        if license_id not in data.get("licenses", {}):
            return False, f"❌ License {license_id} not found"
        
        data["licenses"][license_id]["status"] = "revoked"
        data["licenses"][license_id]["revoked_date"] = datetime.now().isoformat()
        _save_licenses(data)
        
        msg = f"✅ License {license_id} revoked"
        logging.info(f"License revoked by {admin_username}: {license_id}")
        return True, msg
    except Exception as e:
        error_msg = f"❌ Error revoking license: {str(e)}"
        logging.error(error_msg)
        return False, error_msg


def get_license_status(license_id: str, password: str) -> str:
    """
    Get human-readable status of a license.
    """
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





def export_licenses_to_excel(licenses_data: list, filename: str = "commercial_licenses.xlsx") -> Tuple[bool, str]:
    """
    Exports a list of license data to an Excel file.
    """
    try:
        if not licenses_data:
            return False, "No license data to export."
        
        df = pd.DataFrame(licenses_data)
        file_path = os.path.join(LICENSE_DIR, filename)
        df.to_excel(file_path, index=False)
        logging.info(f"Licenses exported to {file_path}")
        return True, f"✅ Licenses successfully exported to {file_path}"
    except Exception as e:
        error_msg = f"❌ Error exporting licenses to Excel: {str(e)}"
        logging.error(error_msg)
        return False, error_msg
