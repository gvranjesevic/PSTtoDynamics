# PST File Analyzer

A Python application for analyzing Microsoft Outlook PST (Personal Storage Table) files and extracting comprehensive email statistics.

## Features

- **📧 Email Extraction**: Recursively extracts emails from all folders and subfolders
- **📊 Comprehensive Statistics**: Provides detailed analytics including:
  - Total email count
  - Emails by folder
  - Top senders
  - Size statistics (total, average, largest)
  - Attachment statistics
  - Date range analysis
- **🔒 Safe Processing**: Handles errors gracefully and provides detailed feedback
- **📋 Clean Output**: Beautiful tabulated reports with emojis for easy reading

## Requirements

- Python 3.7+
- Windows (for PST file access)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/gvranjesevic/PSTtoDynamics.git
   cd PSTtoDynamics
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   **Note**: This project includes multiple implementations:
   - `pst_analyzer_aspose.py` - **Recommended** - Uses Aspose.Email (works well on Windows)
   - `pst_analyzer.py` - Uses pypff (may require compilation on Windows)
   - `pst_analyzer_libratom.py` - Uses libratom (experimental)

## Usage

1. **Place your PST file** in the `PST/` directory (already configured in `.gitignore`)

2. **Run the analyzer**:
   ```bash
   # Recommended - Aspose.Email version (best Windows support)
   python pst_analyzer_aspose.py
   
   # Alternative versions
   python pst_analyzer.py          # pypff version
   python pst_analyzer_libratom.py # libratom version
   ```

3. **View the statistics** in the console output

## Sample Output

```
🔍 PST File Analyzer (Aspose.Email version)
=======================================================
📁 Target PST file: C:\...\PST\gvranjesevic@dynamique.com.001.pst
✅ PST file opened successfully
📧 Starting email extraction...
✅ Extracted 387 emails successfully

============================================================
📊 PST FILE STATISTICS (Aspose.Email version)
============================================================
📧 Total Emails: 387

📁 Emails by Folder:
┌──────────────────────────────────────────────┬─────────────┐
│ Folder                                       │ Email Count │
├──────────────────────────────────────────────┼─────────────┤
│ Top of Personal Folders/.../Contacts        │          50 │
│ Top of Personal Folders/.../Deleted-Items   │          50 │
│ Top of Personal Folders/.../Inbox/NotForMe  │          45 │
└──────────────────────────────────────────────┴─────────────┘

👤 Top 15 Senders:
┌─────────────────────────────┬─────────────┐
│ Sender                      │ Email Count │
├─────────────────────────────┼─────────────┤
│ Djordje ("George")         │          85 │
│ delprem@protective.com      │          42 │
│ Jack LaLonde                │          33 │
└─────────────────────────────┴─────────────┘

🔤 Most Common Subject Words:
┌─────────────┬───────┐
│ Word        │ Count │
├─────────────┼───────┤
│ premium     │    43 │
│ report      │    43 │
│ delinquent  │    42 │
└─────────────┴───────┘
```

## File Structure

```
PSTtoDynamics/
├── pst_analyzer_aspose.py    # Main application (Aspose.Email - Recommended)
├── pst_analyzer.py           # Alternative (pypff)
├── pst_analyzer_libratom.py  # Alternative (libratom)
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .gitignore               # Git ignore rules (excludes PST files)
└── PST/                     # Directory for PST files (not tracked by git)
    └── *.pst                # Your PST files go here
```

## Configuration

The PST file path is configured in the `main()` function of `pst_analyzer.py`. To analyze a different PST file, modify this line:

```python
pst_file_path = r"C:\GitHub-Repos\gvranjesevic@dynamique.com\PSTtoDynamics\PST\your-file.pst"
```

## Troubleshooting

### Common Issues

1. **PST file not found**: Ensure the PST file exists in the specified path
2. **Permission denied**: Run as administrator if needed
3. **pypff import error**: Install pypff-python properly (see installation notes)
4. **Large PST files**: The analysis may take time for large files (>1GB)

### Performance Tips

- For very large PST files, consider running the analysis in chunks
- Ensure adequate free disk space (PST analysis can be memory-intensive)
- Close Outlook while running the analysis to avoid file locks

## Security & Privacy

- PST files are automatically excluded from git tracking via `.gitignore`
- No email content is stored or transmitted - only metadata is analyzed
- All processing is done locally on your machine

## License

This project is open source. Feel free to modify and distribute.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request 

# PST to Dynamics 365

## Overview
A professional desktop application for importing, synchronizing, and managing contacts and emails between PST files and Microsoft Dynamics 365, with advanced AI, analytics, and a modern GUI.

---

## Phase 6: Advanced Sync & Monitoring (NEW)

### Features
- **Bidirectional Sync Engine**: Robust, real-time synchronization between PST and Dynamics 365.
- **Advanced Conflict Resolution**: Last-write-wins, manual, and merge strategies with conflict history.
- **Data Integrity**: Checksums, consistency checks, and recovery mechanisms.
- **Sync Monitoring Dashboard**: Real-time metrics, conflict resolution UI, and detailed logs.
- **Full Integration**: Dashboard accessible from the main navigation sidebar and View menu ("Sync Monitor").

### How to Launch the Sync Monitoring Dashboard
- Start the main application (`python gui/main_window.py` or packaged executable).
- Use the sidebar or View menu to select **Sync Monitor**.
- The dashboard provides:
  - Live sync metrics (syncs, conflicts, errors)
  - Conflict resolution interface
  - Log viewing and export

### Developer Notes
- All new features are unit tested (`tests/test_sync_engine.py`, `tests/test_sync_monitoring_dashboard.py`).
- Modular design for easy extension and integration.

---

## Getting Started
- Install requirements: `pip install -r requirements.txt`
- Run the app: `python gui/main_window.py`

---

## Upcoming: Phase 7 (Deployment & User Experience)
- Windows installer
- Automated deployment
- User onboarding/help
- Feedback and telemetry (optional)
- Production polish

See `PHASE7_PLANNING.md` for details. 