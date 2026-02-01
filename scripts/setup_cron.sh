#!/bin/bash

# Get absolute path to project root
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRAPING_SCRIPT="$PROJECT_DIR/run_scraping.sh"

echo "Setting up periodic scraping..."
echo "Project Directory: $PROJECT_DIR"
echo "Script to run: $SCRAPING_SCRIPT"

# Ensure run_scraping.sh is executable
chmod +x "$SCRAPING_SCRIPT"

# Create logs directory
mkdir -p "$PROJECT_DIR/logs"

# Check if cron is installed (basic check)
if ! command -v crontab &> /dev/null; then
    echo "❌ Error: crontab not found. Please install cron."
    exit 1
fi

# Add to crontab if not already present
# Runs every day at 3:00 AM
CRON_JOB="0 3 * * * $SCRAPING_SCRIPT"

(crontab -l 2>/dev/null | grep -v "$SCRAPING_SCRIPT"; echo "$CRON_JOB") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Cron job added successfully!"
    echo "📅 Schedule: Daily at 3:00 AM"
    echo "📝 Logs will be saved in: $PROJECT_DIR/logs"
    echo "Current crontab:"
    crontab -l | grep "$SCRAPING_SCRIPT"
else
    echo "❌ Failed to add cron job."
fi
