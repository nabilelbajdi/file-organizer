# Intelligent File Organizer

An AI-powered file organization tool that analyzes file content (not just file extensions) and automatically suggests organization categories using local AI models.

## Features

- **Content-Based Analysis**: Uses local AI to analyze actual file content
- **Local AI Only**: Uses Ollama for completely local processing (no cloud services)
- **Interactive & Headless Modes**: Choose between user approval or automatic organization
- **Smart Categorization**: AI suggests meaningful categories and subcategories
- **Dry Run Support**: Preview changes before applying them
- **Rich CLI Interface**: Beautiful terminal interface with progress indicators

## Quick Start

```bash
# Setup (installs Ollama and dependencies)
./setup.sh

# Basic usage - analyze and organize files
python file_organizer.py /path/to/messy/directory

# Preview what would be done (recommended first)
python file_organizer.py /path/to/directory --dry-run

# Automatic organization without prompts
python file_organizer.py /path/to/directory --headless
```

## How It Works

1. **Content Analysis**: Each file is analyzed by local AI
2. **Smart Categorization**: AI suggests categories based on actual content
3. **User Approval**: Interactive approval before moving files
4. **Organization**: Creates organized folder structure

## Requirements

- Python 3.7+
- Ollama (automatically installed by setup script)
- macOS or Linux

## Example Output

```
Intelligent File Organizer - Content-Based Sorting
Target directory: demo_messy_folder
Mode: Interactive (user approval required)

Analyzing actual content of 3 files...
Content Analysis Complete!

Proposed Organization Structure:
  Personal Files/Vacation Photos: 1 files
  Work Documents/Finance: 1 files
  Financial Reports/Company Budget Report: 1 files

Organization Complete!
Files organized in: demo_messy_folder/organized_by_content
``` 