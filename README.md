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

   **Note**: Installing `pypff-python` on Windows can be challenging. If you encounter issues:
   - Try using pre-compiled binaries
   - Consider using Windows Subsystem for Linux (WSL)
   - Alternative: Use `conda install -c conda-forge libpff-python`

## Usage

1. **Place your PST file** in the `PST/` directory (already configured in `.gitignore`)

2. **Run the analyzer**:
   ```bash
   python pst_analyzer.py
   ```

3. **View the statistics** in the console output

## Sample Output

```
🔍 PST File Analyzer
==================================================
📁 Target PST file: C:\...\PST\gvranjesevic@dynamique.com.001.pst
✅ Successfully opened PST file
📧 Starting email extraction...
✅ Extracted 1,234 emails successfully

============================================================
📊 PST FILE STATISTICS
============================================================
📧 Total Emails: 1,234

📁 Emails by Folder:
┌─────────────────┬─────────────┐
│ Folder          │ Email Count │
├─────────────────┼─────────────┤
│ Inbox           │         856 │
│ Sent Items      │         234 │
│ Deleted Items   │         144 │
└─────────────────┴─────────────┘

👤 Top 10 Senders:
┌─────────────────────┬─────────────┐
│ Sender              │ Email Count │
├─────────────────────┼─────────────┤
│ John Doe            │         45  │
│ Jane Smith          │         32  │
└─────────────────────┴─────────────┘
```

## File Structure

```
PSTtoDynamics/
├── pst_analyzer.py      # Main application
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .gitignore          # Git ignore rules (excludes PST files)
└── PST/               # Directory for PST files (not tracked by git)
    └── *.pst          # Your PST files go here
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