# Administrative Scripts

## Available Scripts

### Create Admin User
Creates the first admin account or additional admin users.

```bash
python scripts/create_admin.py
```

Default credentials (if you just press Enter):
- Username: `admin`
- Password: `admin123`

### Cleanup Database
**⚠️ WARNING: Deletes ALL data (reports, pictures, comments)**

```bash
python scripts/cleanup.py
```

You will be prompted to type `DELETE ALL` to confirm.
