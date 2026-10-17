# RetailPulse — Beginner Environment Setup Guide (Windows)

Welcome to **RetailPulse**! This guide walks you through every tool required for this end-to-end retail sales and customer intelligence analytics project.

---

## 1. Overview of Tools Needed

| Tool | Purpose in Project | Is it Free? | How to Install |
| :--- | :--- | :--- | :--- |
| **Python (3.11 or 3.12)** | Data downloading, cleaning, validation, star-schema creation | Free | [python.org](https://www.python.org/downloads/) |
| **SQLite (Built into Python)** | Relational database storage & SQL business queries | Free | Automatically included with Python! |
| **Microsoft Power BI Desktop** | Building interactive 4-page executive dashboards | Free | Microsoft Store or official direct download |
| **Git & GitHub** | Version control & publishing your portfolio repository | Free | [git-scm.com](https://git-scm.com/) |
| **VS Code / IDE** | Viewing code, SQL files, and documentation | Free | [code.visualstudio.com](https://code.visualstudio.com/) |

---

## 2. Step-by-Step Installation Instructions

### Step A: Install Python (Crucial First Step)
1. Visit the official download page: [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Download the latest Python installer (e.g., Python 3.12 for Windows 64-bit).
3. **IMPORTANT (Do not skip this checkbox!)**:
   When the installer opens, look at the bottom of the first window and check the box that says:
   > **[X] Add python.exe to PATH**
4. Click **Install Now**.
5. When the installer finishes, click **Close**.

#### Verify Python on Windows:
Open PowerShell or Command Prompt and type:
```powershell
python --version
pip --version
```
*Expected output: Something like `Python 3.12.x` and `pip 24.x`.*

---

### Step B: Disable Windows Store Python Alias (If "Python was not found" appears)
Windows 10 and 11 have a default shortcut that redirects the word `python` to the Microsoft Store instead of running your installed Python. If you ever encounter that error:
1. Open the Windows **Settings** app (`Win + I`).
2. Go to **Apps** > **Advanced app settings** > **App execution aliases**.
3. Scroll down to:
   - **App Installer (python.exe)** -> Toggle to **OFF**.
   - **App Installer (python3.exe)** -> Toggle to **OFF**.
4. Restart your PowerShell window.

---

### Step C: Install Microsoft Power BI Desktop
Power BI Desktop is the free authoring tool used by Fortune 500 companies and business analysts worldwide.
1. **Method 1 (Recommended - Automatic Updates)**:
   - Open the **Microsoft Store** app on your Windows PC.
   - Search for **Power BI Desktop**.
   - Click **Install / Get**.
2. **Method 2 (Direct Download)**:
   - Go to [https://www.microsoft.com/en-us/download/details.aspx?id=58494](https://www.microsoft.com/en-us/download/details.aspx?id=58494).
   - Download `PBIDesktopSetup_x64.exe` and follow the standard installation wizard.

---

### Step D: Install Project Python Dependencies
Navigate to your project directory in PowerShell:
```powershell
cd c:\Users\USER\Documents\RetailPulse
```

Create a virtual environment (best practice to keep project packages isolated):
```powershell
python -m venv venv
```

Activate the virtual environment:
```powershell
.\venv\Scripts\Activate.ps1
```
*(If PowerShell displays an execution policy error, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` and re-run the activate command).*

Install the required analytical libraries:
```powershell
pip install -r requirements.txt
```

---

## 3. Verifying Your Setup
Run our automated diagnostics script in PowerShell at any time:
```powershell
.\check_env.ps1
```
This script will check your operating system, Python, Pip, Git, network connectivity to the UCI dataset repository, and the project directory structure.
