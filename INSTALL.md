# Installation Guide

## Problem
If you see "pip : 無法辨識" or "Python was not found", Python is not installed on your system.

## Solution: Install Python

### Method 1: Install from Microsoft Store (Recommended, Easiest)

1. Press the `Win` key
2. Search for "Microsoft Store"
3. In the Store, search for "Python 3.12" or "Python"
4. Click "Get" or "Install"
5. Wait for installation to complete

### Method 2: Install from Python Official Website (Recommended, Latest Version)

1. Open your browser and go to: https://www.python.org/downloads/
2. Click "Download Python 3.12.x" (will automatically select the latest version)
3. After download, run the installer
4. **Important**: During installation, make sure to check **"Add Python to PATH"**
5. Click "Install Now" to start installation

## Verify Installation

After installation, please close and reopen PowerShell, then run:

```powershell
python --version
```

If it shows a version number (e.g., `Python 3.12.0`), installation is successful!

## Install Dependencies

After Python is successfully installed, run this command in PowerShell to install required packages:

```powershell
python -m pip install -r requirements.txt
```

Or:

```powershell
pip install -r requirements.txt
```

## If pip still doesn't work

If Python is installed but pip still doesn't work, try:

```powershell
python -m pip install -r requirements.txt
```

This command uses `python -m pip`, which works even if pip is not in PATH.




