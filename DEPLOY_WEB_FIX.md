# Deploy Destination Filter Fix to Digital Ocean

## Quick Deployment Guide

The fix has been pushed to GitHub. Now we need to pull it on your server and restart the web service.

### Option 1: Manual Deployment (Recommended)

1. **Connect to your Digital Ocean server:**
   ```bash
   ssh flights@178.128.241.64
   ```
   Password: `nog3willy3`

2. **Navigate to the application directory:**
   ```bash
   cd /opt/airlines
   ```

3. **Pull the latest changes from GitHub:**
   ```bash
   git pull origin main
   ```

4. **Restart the web service:**
   ```bash
   sudo systemctl restart airlines-web.service
   ```

5. **Verify the service is running:**
   ```bash
   sudo systemctl status airlines-web.service
   ```

6. **Check the logs (optional):**
   ```bash
   sudo journalctl -u airlines-web.service -n 50
   ```

### Option 2: One-Line Deployment

Copy and paste this single command:

```bash
ssh flights@178.128.241.64 "cd /opt/airlines && git pull origin main && sudo systemctl restart airlines-web.service && sudo systemctl status airlines-web.service --no-pager"
```

When prompted, enter password: `nog3willy3`

---

## Testing the Fix

After deployment, visit: **https://alstorphius.com**

1. Change "Vluchttype" to **"Vertrek"** (Departures)
2. The "Bestemming Selectie" section should now appear with dropdowns
3. Select **Continent** → **Country** → **Airport**
4. The rankings should filter to show only flights to that destination

---

## What Was Fixed

### File Changed:
- `web/app.js`

### Issues Resolved:
1. ✅ `destinationsData` variable was undefined
2. ✅ `filters.destination` property was missing
3. ✅ Destination filters not showing/hiding on flight type change
4. ✅ Destinations API not being loaded on startup

### GitHub Commit:
- **Commit ID:** `12921ba`
- **Message:** "Fix: Destination filter not working - Initialize destinationsData and load on startup"
- **Repository:** https://github.com/cleanfield/Airlines

---

## Troubleshooting

### If the filter still doesn't work:

1. **Clear browser cache:**
   - Press `Ctrl + Shift + R` (Windows) or `Cmd + Shift + R` (Mac)

2. **Check if files were updated:**
   ```bash
   ssh flights@178.128.241.64 "cd /opt/airlines && git log --oneline -3"
   ```
   You should see commit `12921ba` at the top.

3. **Verify web service is running:**
   ```bash
   ssh flights@178.128.241.64 "sudo systemctl status airlines-web.service"
   ```

4. **Check Nginx is serving correctly:**
   ```bash
   ssh flights@178.128.241.64 "sudo systemctl status nginx"
   ```

5. **Test API endpoint:**
   ```bash
   curl https://alstorphius.com/api/destinations | jq '. | length'
   ```
   Should return: `9225` (number of destinations)

---

## Alternative: Copy File Directly

If git pull doesn't work for some reason, you can copy the fixed file directly:

```powershell
scp C:\Projects\Airlines\web\app.js flights@178.128.241.64:/opt/airlines/web/app.js
```

Then restart:
```bash
ssh flights@178.128.241.64 "sudo systemctl restart airlines-web.service"
```

---

## Need Help?

If you encounter any issues:

1. Check service logs:
   ```bash
   sudo journalctl -u airlines-web.service -f
   ```

2. Check Nginx error logs:
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

3. Verify file permissions:
   ```bash
   ls -la /opt/airlines/web/app.js
   ```

---

**Last updated:** February 5, 2026  
**Fix version:** v1.0.1
