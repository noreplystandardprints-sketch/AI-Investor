# Commercial License Agreement

## Overview

AI-Investor is available under two licensing models:

1. **CC BY-NC 4.0 (Free)** — For non-commercial use only
2. **Commercial License (Paid)** — For commercial use

## Commercial License

If you wish to use AI-Investor for commercial purposes, you must obtain a commercial license. Commercial use includes, but is not limited to:

- Using the software in a business or revenue-generating context
- Selling products or services that incorporate or rely on AI-Investor
- Using it for trading with capital you intend to profit from
- Providing AI-Investor as part of a commercial service or platform
- Any other use that generates direct or indirect commercial benefit

## License Management System

AI-Investor includes a built-in commercial license tracking system with:

- **Unique License IDs**: Format `AI-INV-XXXXXXXXXX` (randomly generated)
- **Secure Password Protection**: SHA-256 hashed passwords with per-license salts
- **Activation Tracking**: Monitor license usage across multiple instances
- **Expiration Management**: Automatic expiration dates with renewal capability
- **Persistent Storage**: All license data stored in `licenses/commercial_licenses.json`

### License Management Commands

#### Issue a New License (Admin)

```bash
python TradeAI.py --license-action issue \
  --company-name "Acme Trading Corp" \
  --contact-email "legal@acme.com" \
  --use-case "Algorithmic trading on public markets" \
  --expiration-days 365 \
  --max-instances 2
```

Output:
```
🔐 NEW LICENSE CREDENTIALS (share securely via email):
   License ID: AI-INV-F61DBF108751
   Password:   tTYNnH8_VndpVX_seRauUQ
```

#### Verify a License (Customer/Admin)

```bash
python TradeAI.py --license-action verify \
  --license-id AI-INV-F61DBF108751 \
  --license-password tTYNnH8_VndpVX_seRauUQ
```

#### Check License Status

```bash
python TradeAI.py --license-action status \
  --license-id AI-INV-F61DBF108751 \
  --license-password tTYNnH8_VndpVX_seRauUQ
```

#### List All Licenses (Admin)

```bash
python TradeAI.py --license-action list
```

#### Revoke a License (Admin)

```bash
python TradeAI.py --license-action revoke \
  --license-id AI-INV-F61DBF108751
```

## Obtaining a Commercial License

To inquire about commercial licensing options, please contact:

**Email**: [Your contact email]  
**Website**: [Your website or business URL]

### What's Included:

- Unique commercial license with ID and password
- Permission to use AI-Investor commercially
- Permission to modify for internal use
- License activation tracking
- Renewal management
- Optional technical support (negotiable)

### Pricing & Terms:

Commercial licensing terms are negotiated on a case-by-case basis depending on:
- Scale of commercial use
- Distribution scope
- Revenue model
- Support requirements
- Number of instances/deployments

## License File Structure

Commercial licenses are stored in `licenses/commercial_licenses.json`:

```json
{
  "licenses": {
    "AI-INV-F61DBF108751": {
      "license_id": "AI-INV-F61DBF108751",
      "company_name": "TestCorp",
      "contact_email": "test@example.com",
      "commercial_use_case": "Testing",
      "issued_date": "2025-11-14T07:07:08.420631",
      "expiration_date": "2026-11-14T07:07:08.420631",
      "status": "active",
      "max_instances": 1,
      "activations": 0,
      "password_hash": "...",
      "salt": "..."
    }
  },
  "metadata": {
    "last_updated": "2025-11-14T07:07:08.420631"
  }
}
```

## Security

- **Passwords**: Stored as SHA-256 hashes with unique per-license salts
- **File Permissions**: License database restricted to owner (mode 0600)
- **No Plain-text Storage**: Passwords never stored in plain text
- **Activation Limits**: Prevent unauthorized deployments

## Integration with TradeAI

To integrate license verification into your commercial deployments:

```python
from license_tracker import verify_license, activate_license

# Verify license
is_valid, record = verify_license("AI-INV-...", "password")

if is_valid:
    # Activate/log the instance
    success, msg = activate_license("AI-INV-...", "password", "instance-id")
    print(msg)
    # Proceed with commercial features
else:
    print("Invalid license - terminating")
    sys.exit(1)
```

## Dual-Licensing Benefits

### For Users:
- **Free tier**: Full access to the code and features under CC BY-NC 4.0
- **Paid tier**: Commercial rights, support, and optional enhancements

### For Developers:
- Encourage open-source community contributions
- Monetize commercial deployments
- Maintain control over commercial uses

## Questions?

If you're unsure whether your use case requires a commercial license, please reach out. We're happy to clarify.

---

**Last Updated**: November 14, 2025
