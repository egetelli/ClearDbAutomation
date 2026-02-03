This repository contains a Python maintenance script designed to optimize PostgreSQL tables used in a SCADA system. It reduces database size by downsampling high-frequency data and removing duplicate records, ensuring only one data point per minute per signal is retained for historical accuracy.
---

# SCADA Database Cleanup & Optimization Script

This repository contains a Python maintenance script designed to optimize PostgreSQL tables used in a SCADA system. It reduces database size by downsampling high-frequency data and removing duplicate records, ensuring only one data point per minute per signal is retained for historical accuracy.

## 🚀 Features

* **Duplicate Removal:** Deletes duplicate entries in `Values` and `Values_Perm` tables based on `UserSignalID` and timestamp.
* **Downsampling:** Retains only the **first** record recorded within each minute interval.
* **Signal Exclusion:** Respects an exclusion list (`ExcludedSignals` table) to prevent specific critical signals from being cleaned.
* **Automated Time Range:** Automatically targets data from **yesterday** (00:00:00 to 23:59:59).
* **Logging:** Writes detailed success/failure logs to a specified file.
* **Email Notifications:** Sends SMTP email alerts to a distribution list upon completion or failure (including error tracebacks).

## 🛠️ Prerequisites

* **OS:** Windows (implied by the file paths in the script) or Linux.
* **Python:** Version 3.8 or higher.
* **Database:** PostgreSQL.

### Required Python Libraries

You need to install the PostgreSQL adapter. Run the following command:

```bash
pip install psycopg
# or if you are using psycopg2
pip install psycopg2-binary

```

## ⚙️ Configuration

Before running the script, you **must** edit the following variables in the `.py` file to match your environment:

1. **Database Connection:**
Update the `conn_info` string with your server details.
```python
conn_info = "host=127.0.0.1 port=5432 dbname=scada user=postgres password=YOUR_PASSWORD"

```


2. **Log File Path:**
Ensure the directory exists or change the path:
```python
log_file = r"C:\Path\To\Your\Logs\cleanup.log"

```


3. **Email Settings:**
Update the `send_email` function with your SMTP server, credentials, and recipient list.

## ⚠️ Important Note on Data Safety

This script performs **`DELETE`** operations.

* It is designed to keep the *first* record of every minute.
* It specifically skips signals found in the `ExcludedSignals` table.
* **Recommendation:** Always backup your database before running this script for the first time in a production environment.

---

## 📅 How to Automate with Windows Task Scheduler

To run this script automatically every day (e.g., at 03:00 AM), follow these steps:

### 1. Identify Python Path

Open your Command Prompt (cmd) and type `where python`. Note down the full path.

* *Example:* `C:\Users\Admin\AppData\Local\Programs\Python\Python39\python.exe`

### 2. Open Task Scheduler

* Press `Win + R`, type `taskschd.msc`, and press Enter.

### 3. Create a New Task

1. Click **"Create Basic Task..."** in the right-hand Actions pane.
2. **Name:** `SCADA Daily Cleanup`.
3. **Description:** Cleans duplicate SCADA logs for the previous day. Click **Next**.

### 4. Set Trigger

1. Select **Daily**. Click **Next**.
2. Set the **Start time** (e.g., `03:00:00`).
3. Set **Recur every:** `1` days. Click **Next**.

### 5. Set Action

1. Select **Start a program**. Click **Next**.

### 6. Configure Program/Script (Crucial Step)

This is where most errors happen. Fill it out exactly like this:

* **Program/script:** Paste the path to your `python.exe` (found in Step 1).
* *Example:* `C:\Python39\python.exe`


* **Add arguments (optional):** Paste the name of your script file.
* *Example:* `cleanup_script.py`


* **Start in (optional):** Paste the **folder path** where your script is located. **Do not** use quotes here.
* *Example:* `E:\Scada\Scripts\`



> **Why "Start in"?** This ensures that Python can find your script and that the log files are created in the correct relative directory if you used relative paths.

### 7. Finish

Click **Next**, review the settings, and click **Finish**.

### 8. Test It

1. Find your task in the list.
2. Right-click and select **Run**.
3. Check your log file (`E:\Scada\Logs\cleanup_test.log`) to see if it started.
