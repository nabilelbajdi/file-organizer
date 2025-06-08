# Intelligent File Organizer

An AI-powered file organization tool that analyzes file content (not just file extensions) and automatically suggests organization categories using local AI models.

## Features

- **Content-Based Analysis**: Uses local AI to analyze actual file content, not just file extensions
- **Local AI Only**: Uses Ollama for completely local processing (no cloud services)
- **Interactive & Headless Modes**: Choose between user approval or automatic organization
- **Smart Categorization**: AI suggests meaningful categories and subcategories
- **Dry Run Support**: Preview changes before applying them
- **File Type Filtering**: Optionally filter by specific file extensions
- **Rich CLI Interface**: Beautiful terminal interface with progress indicators

## Requirements

- Python 3.7+
- Ollama (automatically installed by setup script)
- macOS or Linux

## Quick Start

1. **Clone and Setup**:
   ```bash
   git clone <your-repo>
   cd intelligent-file-organizer
   ./setup.sh
   ```

2. **Basic Usage**:
   ```bash
   # Analyze and organize files in a directory (interactive mode)
   python3 file_organizer.py /path/to/messy/directory
   
   # Preview what would be done (dry run)
   python3 file_organizer.py /path/to/directory --dry-run
   
   # Automatic organization without user prompts
   python3 file_organizer.py /path/to/directory --headless
   ```

## Command Line Options

```
Usage: file_organizer.py [OPTIONS] DIRECTORY

Options:
  --interactive / --headless     Interactive mode (default) vs headless mode
  --dry-run                      Show what would be done without moving files
  --extensions TEXT              Comma-separated file extensions (e.g., .txt,.py,.md)
  --model TEXT                   Ollama model to use (default: llama3.2:1b)
  --help                         Show this message and exit
```

## Examples

### Interactive Mode (Default)
```bash
python3 file_organizer.py ~/Downloads
```
- Analyzes all files in ~/Downloads
- Shows analysis results in a table
- Asks for confirmation before organizing each category
- Creates organized/ subdirectory with categorized files

### Headless Mode
```bash
python3 file_organizer.py ~/Documents --headless
```
- Automatically organizes files without user prompts
- Good for automated workflows

### Dry Run
```bash
python3 file_organizer.py ~/Desktop --dry-run
```
- Shows what would be done without actually moving files
- Perfect for testing before real organization

### Filter by File Types
```bash
python3 file_organizer.py ~/Projects --extensions .py,.js,.md,.txt
```
- Only analyzes Python, JavaScript, Markdown, and text files

### Use Different AI Model
```bash
python3 file_organizer.py ~/Documents --model llama3.2:3b
```
- Uses a larger, potentially more accurate model

## How It Works

1. **File Discovery**: Scans the specified directory for files
2. **Content Analysis**: Each file is analyzed by the local AI model:
   - Text files: Content is read and analyzed
   - Binary files: File type and metadata are analyzed
3. **Category Suggestion**: AI suggests categories like:
   - `Documents/Work Documents`
   - `Code/Python Scripts`
   - `Images/Screenshots`
   - `Archives/Compressed Files`
4. **Organization**: Files are moved to `organized/` directory with suggested structure
5. **Conflict Resolution**: Duplicate names are handled automatically

## Sample Output

```
Intelligent File Organizer
Directory: /Users/user/Downloads
Mode: Interactive
Model: llama3.2:1b

Scanning for files...
Found 25 files to analyze

Analyzing files with AI...
████████████████████ 100%

┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ File                ┃ Category   ┃ Subcategory    ┃ Confidence ┃ Reason                                          ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ script.py           │ Code       │ Python Scripts │ 95%        │ Python script with data processing functions   │
│ report.pdf          │ Documents  │ Reports        │ 90%        │ PDF document containing business report         │
│ vacation.jpg        │ Images     │ Personal Photos│ 88%        │ JPEG image file, likely personal photograph     │
└─────────────────────┴────────────┴────────────────┴────────────┴─────────────────────────────────────────────────┘

Organization Plan:
  - Code/Python Scripts: 3 files
  - Documents/Reports: 5 files
  - Images/Personal Photos: 8 files

Proceed with file organization? [y/N]: y

Organizing files...
Organization complete!
Files organized in: /Users/user/Downloads/organized
```

## Troubleshooting

### Ollama Connection Issues
```bash
# Check if Ollama is running
ollama list

# Start Ollama service
ollama serve

# Pull required model
ollama pull llama3.2:1b
```

### Permission Issues
```bash
# Make sure you have write permissions to the target directory
chmod u+w /path/to/directory
```

### Python Dependencies
```bash
# Install dependencies manually
pip3 install click ollama rich pathlib2 python-magic
```

## Architecture

The tool consists of several key components:

- **FileAnalyzer**: Interfaces with Ollama to analyze file content
- **FileOrganizer**: Main orchestrator that coordinates the organization process
- **CLI Interface**: Click-based command line interface with rich output
- **Content Detection**: Uses python-magic for file type detection

## Supported Models

Any Ollama-compatible model can be used. Recommended options:
- `llama3.2:1b` (default, fast and lightweight)
- `llama3.2:3b` (more accurate, slower)
- `llama3.1:8b` (most accurate, requires more RAM)