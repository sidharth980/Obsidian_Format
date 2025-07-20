# Obsidian Vault Organizer

A Python tool that uses Large Language Models (LLMs) to intelligently organize your Obsidian vault by analyzing file names and suggesting better folder structures.

## 🔒 Privacy & Data Security

**Important**: This tool only analyzes **file names and folder structures** from your Obsidian vault. The **content inside your files is never read or sent to any AI service**. Only the following information is used for organization suggestions:

- File names
- Current folder structure
- File sizes (for reference)

Your personal notes and content remain completely private and local to your machine.

## Features

- 🤖 AI-powered organization suggestions using Google Gemini or Anthropic Claude
- 📁 Automatic folder creation and file movement
- 💾 Automatic backup creation before reorganization
- 📊 Detailed organization report generation
- 🧹 Cleanup of empty directories
- ⚡ Fast indexing of large vaults

## Prerequisites

- Python 3.7 or higher
- Google API key (for Gemini) or Anthropic API key (for Claude)
- Obsidian vault directory

## Installation

1. **Clone or download this repository**

2. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Setup

### For Google Gemini (Recommended)

1. Get a Google API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Use the `format-google.py` script

### For Anthropic Claude

1. Get an Anthropic API key from [Anthropic Console](https://console.anthropic.com/)
2. Use the `format-anthropic.py` script

## Usage

### Using Google Gemini

```bash
python Obsidian/format-google.py /path/to/your/vault --api-key YOUR_GOOGLE_API_KEY
```

### Using Anthropic Claude

```bash
python Obsidian/format-anthropic.py /path/to/your/vault --api-key YOUR_ANTHROPIC_API_KEY
```

### Options

- `--no-backup`: Skip creating a backup before reorganization
- `--api-key`: Your API key (required)

## Example Usage

```bash
# Organize vault with backup (recommended)
python Obsidian/format-google.py ~/Documents/ObsidianVault --api-key YOUR_API_KEY

# Organize without backup (use with caution)
python Obsidian/format-google.py ~/Documents/ObsidianVault --api-key YOUR_API_KEY --no-backup
```

## How It Works

1. **Indexing**: Scans your vault and creates a list of all markdown files with their current locations
2. **AI Analysis**: Sends file structure (names only) to the AI service for organization suggestions
3. **Backup**: Creates a timestamped backup of your current vault structure
4. **Confirmation**: Shows you the proposed organization plan and asks for confirmation
5. **Reorganization**: Moves files to their new locations and creates necessary folders
6. **Cleanup**: Removes empty directories and generates a detailed report

## Output Files

- **Backup**: `obsidian_vault_backup_YYYYMMDD_HHMMSS/` in your vault's parent directory
- **Report**: `_organization_report.md` in your vault root with details of all changes

## Safety Features

- ✅ Automatic backup creation before any changes
- ✅ User confirmation required before reorganization
- ✅ Only moves files, never deletes
- ✅ Preserves all file content
- ✅ Creates detailed logs of all changes

## Troubleshooting

### Common Issues

1. **"No markdown files found"**: Ensure your vault contains `.md` files
2. **API key errors**: Verify your API key is correct and has sufficient credits
3. **Permission errors**: Ensure you have write permissions to your vault directory

### Getting Help

- Check the generated `_organization_report.md` for details about what was changed
- Restore from the backup if needed: `cp -r obsidian_vault_backup_* /path/to/restore/`

## Requirements

Create a `requirements.txt` file with:

```
google-generativeai>=0.3.0
anthropic>=0.7.0
```

## License

This project is open source. Feel free to modify and distribute according to your needs.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

---

**Note**: Always test with a small vault first to ensure the organization suggestions meet your expectations. 