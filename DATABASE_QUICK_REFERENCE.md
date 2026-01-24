# Database Quick Reference

## Connection Test

```bash
wsl bash -c "cd /mnt/c/Projects/Airlines && source venv/bin/activate && python main.py db-test"
```

## Process Data with Database Save

```bash
# Process departures and save to database
wsl bash -c "cd /mnt/c/Projects/Airlines && source venv/bin/activate && python main.py process departures 2026-01-22_to_2026-01-22"

# Process arrivals and save to database
wsl bash -c "cd /mnt/c/Projects/Airlines && source venv/bin/activate && python main.py process arrivals 2026-01-22_to_2026-01-22"
```

## Process Data WITHOUT Database (CSV only)

```bash
wsl bash -c "cd /mnt/c/Projects/Airlines && source venv/bin/activate && python main.py process departures 2026-01-22_to_2026-01-22 --no-db"
```

## Database Configuration

All database settings are in `.env`:

- `MARIA_SERVER` - Database server IP/hostname
- `MARIA_SSH_USER` - SSH username
- `MARIA_ID_ED25519` - Path to SSH private key (WSL format)
- `MARIA_SSH_PASSPHRASE` - SSH key passphrase
- `MARIA_DB` - Database name
- `MARIA_DB_USER` - Database username
- `MARIA_DB_PASSWORD` - Database password

## Database Tables

### flights

Stores individual flight records with:

- Flight details (number, airline, direction)
- Schedule and actual times
- Delay calculations
- Operational info (terminal, gate, etc.)

### airline_statistics

Stores aggregated airline performance metrics:

- Total flights and on-time flights
- Average, median, min, max delays
- On-time percentage
- Reliability score
- Date range for the statistics

## Direct Database Access (if needed)

```bash
# Connect via SSH tunnel manually
ssh -L 3306:127.0.0.1:3306 <ssh_user>@<server_ip>

# Then in another terminal:
mysql -h 127.0.0.1 -u <db_user> -p <database_name>
```

## Troubleshooting

### Connection Issues

1. Check SSH key permissions: `chmod 600 ~/.ssh/id_ed25519`
2. Verify .env file has correct WSL paths
3. Test SSH connection: `ssh <ssh_user>@<server_ip>`

### Data Not Saving

1. Check for error messages in output
2. Verify datetime formats are correct
3. Use `--no-db` flag to test processing without database

### Performance

- Database saves add ~5-10 seconds per processing run
- 200 flights = ~181 database inserts/updates
- Uses ON DUPLICATE KEY UPDATE for idempotent operations
