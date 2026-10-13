# DaVinci Writer - Quick Start Guide

## 🚀 Windows Users

### Starting DaVinci Writer

Simply **double-click** `start.bat` in the folder root.

This will:
1. ✓ Check if Python is installed
2. ✓ Create or activate the virtual environment
3. ✓ Check dependencies (installs on first run or when requirements change)
4. ✓ Start the application
5. ✓ Open your browser automatically to http://localhost:8501
6. ✓ Show progress in a terminal window

**Terminal Output Example:**
```
==========================================
  DaVinci Writer -- Startup Progress
==========================================

[1/6] Checking Python version...
[1/6] Python 3.11.7 found ✓

[2/6] Virtual environment exists ✓

[3/6] Dependencies already up to date ✓

[4/6] Checking configuration...
[4/6] Configuration file found ✓

[5/6] Starting application in background...
[5/6] Application process started ✓

[6/6] Waiting for application to be ready on http://localhost:8501...
[6/6] Application is ready ✓

 ============================================
  DaVinci is running!
  URL: http://localhost:8501
  To stop: run stop.bat
 ============================================
```

On Windows the app runs in the background, so you can close the progress window once it says the app is running. On first run, phase 3 can take 5–15 minutes while dependencies install.

### Stopping DaVinci Writer

Simply **double-click** `stop.bat` in the folder root.

This will:
1. ✓ Check if the application is running
2. ✓ Send a stop signal
3. ✓ Verify the port is released
4. ✓ Show progress in a terminal window

**Terminal Output Example:**
```
==========================================
  DaVinci Writer - Stopping
==========================================

[1/3] Checking if application is running...
[1/3] Application found running on port 8501 ✓

[2/3] Stopping application...
[2/3] Stop signal sent ✓

[3/3] Verifying application stopped...
[3/3] Port 8501 is now free ✓

==========================================
  Application stopped successfully!
==========================================
```

---

## 🍎 macOS Users

### Starting DaVinci Writer

**Double-click** `Start DaVinci.command` in the folder root.

Or from Terminal:
```bash
./Start\ DaVinci.command
```

This will:
1. ✓ Check if Python 3 is installed
2. ✓ Create or reuse the virtual environment
3. ✓ Install dependencies only when needed (first run or when `web/requirements.txt` changes)
4. ✓ Check for a `.env` configuration file
5. ✓ Free port 8501 (stops any previous DaVinci instance)
6. ✓ Start the application and open your browser automatically to http://localhost:8501

> **Keep the Terminal window open while you work.** On macOS the app runs inside that window — closing it (or pressing `Ctrl+C`) stops DaVinci. Use `Stop DaVinci.command` for a clean shutdown.

### Stopping DaVinci Writer

**Double-click** `Stop DaVinci.command` in the folder root.

Or from Terminal:
```bash
./Stop\ DaVinci.command
```

This will:
1. ✓ Check if the application is running
2. ✓ Send a stop signal
3. ✓ Verify the port is released
4. ✓ Show progress in a Terminal window

---

## 📊 What Happens During Startup

### Phase 1: Python Check (1 second)
- Verifies Python 3.10+ is installed
- Shows Python version

### Phase 2: Virtual Environment (5 seconds)
- Creates `.venv/` if needed
- Activates the virtual environment

### Phase 3: Dependencies (5-15 minutes on first run)
- Installs required Python packages (streamlit, anthropic, python-dotenv, etc.)
- Runs only when needed: first run, missing packages, or when `web/requirements.txt` changes
- Usually very fast on repeat runs when dependencies are already up to date

### Phase 4: Configuration (1 second)
- Checks for `.env` file with API keys
- Uses defaults if not found

### Phase 5: Application Start (2 seconds)
- Windows: launches the Streamlit application hidden in the background (output goes to `.davinci.log`)
- macOS: first frees port 8501, then runs the application in the Terminal window
- Starts listening on http://localhost:8501

### Phase 6: Ready Check (5-20 seconds, Windows)
- Waits until port 8501 is listening
- Opens your default browser when ready (on macOS the browser opens a few seconds after the app starts)

---

## 🛑 What Happens During Shutdown

### Phase 1: Check Status (1 second)
- Verifies if application is running
- Shows what's currently on port 8501

### Phase 2: Stop Signal (1 second)
- Sends process termination signals for app PIDs using the OS-native command (`taskkill` on Windows, `kill` on macOS)
- Uses short retry loops to confirm shutdown and escalates only when needed

### Phase 3: Verification (1 second)
- Confirms port 8501 is now free
- Reports success or warns if port is still in use after retries

---

## 🆘 Troubleshooting

### "Python not found"
- Install Python 3.10 or later from https://www.python.org/
- Make sure to check "Add Python to PATH" during installation

### Application takes a long time to start
- First run can take 5-15 minutes as it installs dependencies
- It can also take longer after changing `web/requirements.txt` because dependencies are refreshed
- Check your internet connection
- Subsequent runs should be much faster (30-60 seconds)

### "Port 8501 is already in use"
- Another instance of DaVinci is running
- Run `stop.bat` (Windows) or `Stop DaVinci.command` (macOS) first
- On macOS, `Start DaVinci.command` already stops any process on port 8501 before starting
- Or restart your computer

### Browser doesn't open automatically
- Check that a browser is installed and set as default
- Manually open http://localhost:8501 in your browser

### Application crashes or won't start
- Windows: Check `.davinci.log` file in the root folder
- macOS: Check the Terminal output for error messages
- Try running `stop.bat` / `Stop DaVinci.command` and then `start.bat` / `Start DaVinci.command` again

---

## 📝 Advanced: Running from Command Line

### Windows (PowerShell)
```powershell
# Start
.\start.bat

# Stop
.\stop.bat

# Check status
netstat -ano | findstr ":8501"
```

### macOS / Linux (Bash)
```bash
# Start
./Start\ DaVinci.command

# Stop
./Stop\ DaVinci.command

# Check status
lsof -i :8501
```

---

## ✅ Verification Checklist

- [ ] `start.bat` launches a terminal with progress
- [ ] Terminal shows 6 phases of startup
- [ ] Browser opens to http://localhost:8501
- [ ] Application is visible and responsive
- [ ] `stop.bat` launches a terminal with progress
- [ ] Terminal shows stopping progress
- [ ] Application closes
- [ ] Port 8501 is released

---

## 📞 Getting Help

If you encounter issues:

1. **Check the terminal output** - Error messages show the exact problem
2. **Look at the log file** - Windows: `.davinci.log` (if created)
3. **Try stop then start** - This resolves many issues
4. **Restart your computer** - Clears ports and processes

For persistent issues, provide:
- The complete terminal output
- Your operating system and version
- Python version (`python --version`)
- Any error messages you see

---

**Happy writing! 🎉**
