#!/bin/bash
cd /root/clawd
python3 torn_reporter.py >> reports/torn_status_report_$(date +%Y%m%d).log 2>&1
