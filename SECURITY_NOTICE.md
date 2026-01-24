# Security Notice

## Credentials Management

**IMPORTANT**: All actual credentials have been removed from documentation files for security.

### Where Credentials Are Stored

Actual credentials are **ONLY** stored in:

- `.env` file (which is in `.gitignore` and NOT committed to git)
- `.env.backup` (local backup, also in `.gitignore`)

### Documentation Files

All `.md` documentation files use **placeholders** instead of actual credentials:

- `<server_ip>` instead of actual IP address
- `<password>` instead of actual passwords
- `<ssh_user>` instead of actual SSH username
- `<db_user>` instead of actual database username
- `<username>` instead of actual system username

### Setting Up Credentials

When setting up the project on a new system:

1. Copy `.env.example` to `.env`
2. Edit `.env` and replace placeholders with your actual credentials
3. **NEVER** commit `.env` to version control
4. **NEVER** include actual credentials in documentation

### Sanitization Script

If you accidentally add credentials to documentation, run:

```bash
wsl bash sanitize_docs.sh
```

This will replace all known credential patterns with placeholders.

### Best Practices

1. ✅ Keep credentials in `.env` file only
2. ✅ Use placeholders in all documentation
3. ✅ Add `.env` to `.gitignore`
4. ✅ Use environment-specific `.env` files for different deployments
5. ❌ Never hardcode credentials in source code
6. ❌ Never commit credentials to git
7. ❌ Never share credentials in documentation or chat

### Verification

To verify no credentials are in documentation:

```bash
# Check for IP address
grep -r "178.128.241.64" *.md

# Check for password
grep -r "nog3willy3" *.md

# Should return no results if properly sanitized
```

## What to Do If Credentials Are Exposed

If credentials are accidentally committed or exposed:

1. **Immediately** change all passwords
2. **Rotate** SSH keys
3. **Review** git history and remove exposed credentials
4. **Update** `.env` with new credentials
5. **Notify** team members if applicable

## Environment Variables Reference

See `.env.example` for the complete list of required environment variables with placeholder values.
