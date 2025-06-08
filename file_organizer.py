#!/usr/bin/env python3
"""
Intelligent File Organizer - VG Assignment
Terminal program to organize files by content using local AI

VG Requirements:
- Go through folder structure and sort files by actual content
- Unknown categories at start - program suggests organization
- CLI flags for headless/interactive modes
- User approval of sorting policy
- Only local AI usage
"""

import os
import click
import ollama
from pathlib import Path
from typing import List, Dict


class FileContentAnalyzer:
    """Analyzes file content using local AI to determine categories"""
    
    def __init__(self, model_name: str = "llama3.2:1b"):
        self.model_name = model_name
        self.client = ollama.Client()
        
    def verify_local_ai_connection(self) -> bool:
        """Verify that local AI (Ollama) is running and model is available"""
        try:
            models_response = self.client.list()
            print(f"Local AI connection verified - Available models found")
            return True
        except Exception as e:
            print(f"Error connecting to local AI (Ollama): {e}")
            return False


class FileOrganizer:
    """Main organizer class that implements file discovery"""
    
    def __init__(self, target_directory: Path):
        self.target_directory = Path(target_directory)
        self.analyzer = FileContentAnalyzer()
        
    def discover_all_files(self) -> List[Path]:
        """Discover ALL files in folder structure - VG requirement"""
        discovered_files = []
        
        print(f"Scanning directory: {self.target_directory}")
        
        for root, dirs, filenames in os.walk(self.target_directory):
            # Skip hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for filename in filenames:
                # Skip hidden files
                if filename.startswith('.'):
                    continue
                    
                file_path = Path(root) / filename
                discovered_files.append(file_path)
                    
        return discovered_files


@click.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--headless', is_flag=True, default=False, 
              help='Headless mode: no user interaction, automatic execution')
@click.option('--dry-run', is_flag=True, help='Show what would be done without moving files')
def main(directory, headless, dry_run):
    """
    Intelligent File Organizer - VG Assignment Implementation
    
    DIRECTORY: Target directory to organize
    """
    print("Intelligent File Organizer - Content-Based Sorting")
    print(f"Target directory: {directory}")
    print(f"Mode: {'Headless (automatic execution)' if headless else 'Interactive (user approval required)'}")
    
    if dry_run:
        print("DRY RUN MODE - No files will be moved")
    
    print("\nVG Assignment Requirements:")
    print("- Analyzing ACTUAL file content (not extensions)")
    print("- Unknown categories at start - AI determines organization") 
    print("- Using ONLY local AI (Ollama)")
    print("- Content-based sorting with user approval")
    
    # Initialize organizer
    organizer = FileOrganizer(Path(directory))
    
    # Verify local AI connection - REQUIREMENT: only local AI
    print(f"\nVerifying local AI connection...")
    if not organizer.analyzer.verify_local_ai_connection():
        print("FAILED: Cannot connect to local AI (Ollama)")
        print("Requirements: Local AI must be running")
        print("Solution: Start Ollama with 'ollama serve'")
        return
    
    print(f"\nDiscovering files in folder structure...")
    all_files = organizer.discover_all_files()
    print(f"Found {len(all_files)} files to analyze")
    
    if not all_files:
        print("No files found to organize")
        return
        
    # List discovered files
    print("\nDiscovered files:")
    for file_path in all_files:
        rel_path = file_path.relative_to(organizer.target_directory)
        print(f"  - {rel_path}")
    
    print("\nFile discovery complete! Next: Add content analysis...")

if __name__ == "__main__":
    main()