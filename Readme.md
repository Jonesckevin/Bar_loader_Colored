# Python GUI - Barbell Calculator and Powerlifting Management 

## Author

Created by **JonesCKevin**.  
GitHub Repository: [Bar_loader_Colored](https://github.com/Jonesckevin/Bar_loader_Colored)

<div style="border: 5px solid rgb(14, 202, 68);
border-radius: 0 35px 0 35px;
box-shadow: 5px 5px 15px rgba(0, 0, 0, 0.5); display: inline-block;">
    <img src="Example/ui_photo.png" alt="Barbell Calculator UI" style="display: block; border-radius: 0 25px 0 25px;">
</div>

## Overview

The **Barbell Calculator** is a python script using [Qt6](https://www.pythonguis.com/pyqt6-tutorial/) to create a GUI visual aid for weightlifting enthusiasts. It helps calculate barbell weights and provides a customizable theme interface. It also has a second tab for managing users, to add, edit, remove, import, export, and purge users. The app is designed to be user-friendly with an interactive UI that allows you to adjust weights and view user details easily.

> The program does not currently save data on close.

## Features

- Window Resizing
- Hide User management tab
- Pop-out Stopwatch with start/stop/reset functionality.
- Pop-out Timer with start/stop/reset functionality.
- Link to a powerlifting rules.  (Change as you see fit)
- Calculate weights in lbs, kg, or stones.
- Round weights for precision.
- Choose or create custom bars and colors, or dumbbell themes.
- Weight preview and popout preview available
- Interactive UI with weight adjustment buttons.
- Double Click Manage users: add, edit, remove, import, export
- Edit user data in a dialog.
- Purge users with auto-backup.
- Import users from CSV (replace).
- Export users from CSV.
- Add users with via dialog box.
- View user details in a dialog.
- Filter user data
- Sort users by name, weight, or any column.
- Auto populate user weight (other weight) when adding users.
- Remove users with confirm overide (archived in `data/removed.csv`)
- Cycle users with "Prev"/"Next" and see details.
- "Up Next" preview for the next user.
- User data stored in `data` for easy backup.
- Auto-create `data` and example users if missing.
- Archived and purged users are backed up.
- **User table now displays all major powerlifting scoring systems:**
  - DOTS (primary)
  - Wilks (original)
  - Wilks2 (updated)
  - IPF Points
  - IPF GL Points
- **Sort and filter users by any scoring system.**
- **All scoring columns are automatically calculated and updated.**

### Creating your own theme

1. Create a new theme folder in the `BarBellWeights` directory. The name should start with `lb_` or `kg_` to indicate the weight type. Otherwise, the theme will go to the All/Other filter.
2. Copy one of the examples for quicker results, but ensure you have a `bar.png`, `none.png`, and the files should be named by their weight type (e.g., `45.png`, `47.5.png`).
3. I recommend putting weights from `45 to 855 for barbell` or `5 to 120 for dumbbell`.
4. If you want to add your theme or make changes, just create a pull request.

## Preperations / Installation

Installs `python` and `pip` along with all required packages and dependencies.

### Using PowerShell (Windows)

```powershell
.\setup.ps1
```

### Using Bash (Linux/MacOS)

```bash
bash setup.sh
```

### Create exe from Python script

```powershell
.\build_exe.bat
```

## Data Directory

- All user data (`users.csv`, `removed.csv`, backups) is stored in the `data` directory.
- The app will auto-create `data/users.csv` with example users if it does not exist.
- This keeps user data separate from resources and themes.

## Ideas
- Add a hotkey mapping config file and allow users to use the gui to map on the fly.
- Add Gui customizations

## To Do

- Add Judge and Referee management.
- Add Live Scoring & Results Display
- Add Rack Height Management
- Custom Branding & Sponsorships Loading
- Help Menus
- Create Graphics for Competitor Results and stats
- Hotkey for Judges
