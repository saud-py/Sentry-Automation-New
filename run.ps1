# PowerShell script to run Sentry Alert Automation with proper encoding
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

# Run the main script with all arguments passed through
python src/main.py $args 