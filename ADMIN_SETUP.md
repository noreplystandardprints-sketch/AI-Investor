# AI-Investor License Administration Guide

## Overview

This guide explains how to set up and manage commercial licenses for AI-Investor. Only you (the admin) can issue, revoke, and manage licenses.

## Admin Setup (One-Time)

### Step 1: Initialize Admin Credentials

Run this command ONCE to set up your admin account:

```bash
python TradeAI.py --license-action admin-init
```

Output:
```
Set admin username: myusername
Set admin password (will be hashed): ••••••••••
✅ Admin credentials saved securely
```

This creates `licenses/admin_credentials.json` (restricted to owner only).

### Step 2: Verify Admin Setup

Admin credentials are stored securely:
- **Location**: `licenses/admin_credentials.json` (mode 0600 — owner read/write only)
- **Password**: SHA-256 hashed with unique salt
- **Logging**: All admin actions logged to `licenses/admin_actions.log`

**WARNING**: Do NOT share your admin credentials. They provide full control over all licenses.

---

## Adding Commercial Users (Issuing Licenses)

### Issue a New Commercial License

```bash
python TradeAI.py --license-action issue \
  --admin-username myusername \
  --admin-password "••••••••••" \
  --company-name "Acme Trading Corp" \
  --contact-email "legal@acme.com" \
  --use-case "Algorithmic trading on public markets" \
  --expiration-days 365 \
  --max-instances 2
```

**Output:**
```
✅ License issued: AI-INV-F61DBF108751
Company: Acme Trading Corp
Expiration: 2026-11-14T07:07:08.420631

🔐 NEW LICENSE CREDENTIALS (share securely via email):
   License ID: AI-INV-F61DBF108751
   Password:   tTYNnH8_VndpVX_seRauUQ
```

### Required Parameters

- `--admin-username`: Your admin username (created during admin-init)
- `--admin-password`: Your admin password
- `--company-name`: Name of the company/user buying the license
- `--contact-email`: Their contact email
- `--use-case`: Description of intended commercial use
- `--expiration-days`: How many days until expiration (default: 365)
- `--max-instances`: Maximum deployments allowed (default: 1)

### Sharing License Credentials with Users

1. Copy the License ID and Password from the output
2. Send to the customer via **secure channel** (encrypted email, secure message)
3. **DO NOT** include credentials in logs or version control

Example email template:

```
Subject: Your AI-Investor Commercial License

Dear [Company],

Your commercial license for AI-Investor is ready to use.

License ID: AI-INV-F61DBF108751
Password:   tTYNnH8_VndpVX_seRauUQ

To activate your license, run:

    python TradeAI.py --license-action verify \
      --license-id AI-INV-F61DBF108751 \
      --license-password tTYNnH8_VndpVX_seRauUQ

For support, contact: [your email]

Best regards,
AI-Investor Team
```

---

## Managing Existing Licenses

### List All Commercial Licenses

```bash
python TradeAI.py --license-action list \
  --admin-username myusername \
  --admin-password "••••••••••"
```

**Output:**
```
================================================================================
Commercial Licenses (3 total)
================================================================================

License ID: AI-INV-F61DBF108751
  Company: Acme Trading Corp
  Email: legal@acme.com
  Status: active
  Expires: 2026-11-14T07:07:08.420631
  Activations: 2/2
  
License ID: AI-INV-2B3C4D5E6F7A8
  Company: TechFunds Inc
  Email: trading@techfunds.com
  Status: active
  Expires: 2025-12-15T10:30:00.000000
  Activations: 1/5

================================================================================
```

### Check License Status (Customer View)

Customers can check their own license status:

```bash
python TradeAI.py --license-action status \
  --license-id AI-INV-F61DBF108751 \
  --license-password tTYNnH8_VndpVX_seRauUQ
```

**Output:**
```
✅ Valid license for Acme Trading Corp
Expires: 2026-11-14T07:07:08.420631
Activations: 2/2
```

### Revoke a License (Disable Customer Access)

```bash
python TradeAI.py --license-action revoke \
  --admin-username myusername \
  --admin-password "••••••••••" \
  --license-id AI-INV-F61DBF108751
```

**Output:**
```
✅ License AI-INV-F61DBF108751 revoked
```

After revocation:
- The license becomes inactive
- Customer attempts to verify will fail
- License marked as "revoked" in the database

---

## License Data Storage & Backup

### Where License Data is Stored

```
licenses/
├── commercial_licenses.json    # All active/revoked licenses
├── admin_credentials.json      # Admin credentials (mode 0600)
└── admin_actions.log           # Audit log of all admin actions
```

### License File Structure

`licenses/commercial_licenses.json`:

```json
{
  "licenses": {
    "AI-INV-F61DBF108751": {
      "license_id": "AI-INV-F61DBF108751",
      "company_name": "Acme Trading Corp",
      "contact_email": "legal@acme.com",
      "commercial_use_case": "Algorithmic trading on public markets",
      "issued_date": "2025-11-14T07:07:08.420631",
      "expiration_date": "2026-11-14T07:07:08.420631",
      "status": "active",
      "max_instances": 2,
      "activations": 2,
      "last_activation": "2025-11-14T08:30:00.000000",
      "last_instance": "user-instance-2",
      "password_hash": "a7f3c8e9...",
      "salt": "b4d2e1f5..."
    }
  },
  "metadata": {
    "last_updated": "2025-11-14T08:30:00.000000"
  }
}
```

### Audit Logging

All admin actions are logged to `licenses/admin_actions.log`:

```
2025-11-14 07:07:08,420 - INFO - Admin initialized: myusername
2025-11-14 07:08:15,630 - INFO - Admin authenticated: myusername
2025-11-14 07:08:20,450 - INFO - License issued by myusername: AI-INV-F61DBF108751 for Acme Trading Corp
2025-11-14 07:09:30,210 - INFO - License verified: AI-INV-F61DBF108751
2025-11-14 07:10:45,890 - WARNING - Failed admin login attempt: wrong password for myusername
```

### Backup Recommendations

1. **Regular Backups**: Backup `licenses/` directory weekly
   ```bash
   cp -r licenses/ licenses_backup_$(date +%Y%m%d).zip
   ```

2. **Version Control**: You may want to `.gitignore` commercial_licenses.json to avoid accidental commits:
   ```bash
   echo "licenses/commercial_licenses.json" >> .gitignore
   echo "licenses/admin_credentials.json" >> .gitignore
   ```

3. **Offsite Storage**: Keep encrypted copies in secure cloud storage

---

## Security Best Practices

### Admin Credentials

- ✅ Use a **strong admin password** (16+ characters, mixed case, numbers, symbols)
- ✅ Store admin password securely (password manager)
- ✅ **Never** hardcode admin credentials in scripts or environment
- ❌ **Don't** share admin credentials with customers
- ❌ **Don't** commit `admin_credentials.json` to version control

### Customer Credentials

- ✅ Send license credentials via **encrypted channels** only
- ✅ Use unique passwords for each license
- ✅ Include expiration dates so licenses expire automatically
- ✅ Revoke licenses when customers stop paying

### File Permissions

- `admin_credentials.json` is automatically set to `0600` (owner read/write only)
- `commercial_licenses.json` is automatically set to `0600`
- Verify permissions regularly:
  ```bash
  ls -la licenses/
  # Should show: -rw------- (600)
  ```

---

## Troubleshooting

### "Admin not initialized"

**Problem**: You haven't set up admin credentials yet

**Solution**: Run `python TradeAI.py --license-action admin-init`

### "Admin authentication failed"

**Problem**: Wrong admin username or password

**Solution**: Check your credentials and try again

### "License not found"

**Problem**: License ID doesn't exist or was mistyped

**Solution**: Run `python TradeAI.py --license-action list` to see all licenses

### "License activation limit exceeded"

**Problem**: Customer is trying to activate license on too many instances

**Solution**: 
1. Check current activations: `python TradeAI.py --license-action list`
2. Either increase `--max-instances` or revoke old activations

### Corrupted `commercial_licenses.json`

**Problem**: The licenses file is corrupted or invalid JSON

**Solution**:
1. Restore from backup: `cp licenses_backup_YYYYMMDD.json licenses/commercial_licenses.json`
2. Or manually edit the JSON file to fix syntax errors

---

## Advanced: Integrating License Checks into Your Trading Bot

To require a valid commercial license before running trading features:

```python
from license_tracker import verify_license

def validate_commercial_license(license_id, password):
    """Check license before running commercial features."""
    is_valid, record = verify_license(license_id, password)
    
    if not is_valid:
        print("❌ Invalid license")
        return False
    
    # Check if expired
    exp_date = datetime.fromisoformat(record['expiration_date'])
    if datetime.now() > exp_date:
        print("❌ License expired")
        return False
    
    # Log successful activation
    from license_tracker import activate_license
    success, msg = activate_license(license_id, password, "deployment-instance-1")
    print(msg)
    
    return success
```

Then use it before enabling commercial features:

```python
if IBKR_EXECUTE and not validate_commercial_license(license_id, password):
    sys.exit(1)
```

---

## Support & Questions

For license management issues:
1. Check the audit log: `cat licenses/admin_actions.log`
2. Verify file permissions: `ls -la licenses/`
3. Review this guide thoroughly
4. Contact support with specific error messages

---

**Last Updated**: November 14, 2025
