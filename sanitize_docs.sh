#!/bin/bash
# Script to remove credentials from all markdown files

echo "Sanitizing credentials from documentation files..."

# Replace IP address
find . -name "*.md" -type f -exec sed -i 's/178\.128\.241\.64/<server_ip>/g' {} \;

# Replace password
find . -name "*.md" -type f -exec sed -i 's/OLD_PASSWORD/<password>/g' {} \; # Please manually update OLD_PASSWORD if needed

# Replace username in SSH commands
find . -name "*.md" -type f -exec sed -i 's/flights@<server_ip>/<ssh_user>@<server_ip>/g' {} \;

# Replace specific user path
find . -name "*.md" -type f -exec sed -i 's/\/mnt\/c\/Users\/vandi/\/mnt\/c\/Users\/<username>/g' {} \;
find . -name "*.md" -type f -exec sed -i 's/C:\\\\Users\\\\vandi/C:\\Users\\<username>/g' {} \;

echo "Done! Credentials have been replaced with placeholders."
echo "Please review the changes and commit them."
