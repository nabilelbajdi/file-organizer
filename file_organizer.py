#!/usr/bin/env python3
"""
Intelligent File Organizer
An AI-powered file organization tool that analyzes file content and automatically 
suggests organization categories using local AI models.

Features:
- Content-based analysis (not just file extensions)
- Local AI processing for privacy
- Interactive and headless operation modes
- Smart categorization with confidence scoring
- Dry-run capability for safe testing
"""

import os
import shutil
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import sys

import click
import ollama
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.prompt import Confirm

try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False
    print("Warning: python-magic not available. File type detection will be limited.")

console = Console()


class FileContentAnalyzer:
    """Analyzes file content using local AI to determine categories"""
    
    def __init__(self, model_name: str = "llama3.2:1b"):
        self.model_name = model_name
        self.client = ollama.Client()
        
    def verify_local_ai_connection(self) -> bool:
        """Verify that local AI (Ollama) is running and model is available"""
        try:
            models_response = self.client.list()
            
            # Handle different response formats
            if hasattr(models_response, 'models'):
                available_models = [model.model for model in models_response.models]
            elif isinstance(models_response, dict) and 'models' in models_response:
                available_models = [model['name'] for model in models_response['models']]
            else:
                available_models = []
                
            if self.model_name not in available_models:
                console.print(f"[yellow]Model {self.model_name} not found. Available models: {available_models}")
                console.print(f"[blue]Attempting to pull {self.model_name}...")
                self.client.pull(self.model_name)
            return True
        except Exception as e:
            console.print(f"[red]Error connecting to local AI (Ollama): {e}")
            return False
    
    def extract_file_content(self, file_path: Path, max_chars: int = 2000) -> str:
        """Extract file content for AI analysis - actual content, not just extension"""
        try:
            # Detect file type by content, not extension
            if HAS_MAGIC:
                file_type = magic.from_file(str(file_path), mime=True)
            else:
                # Fallback: basic extension-based detection
                ext = file_path.suffix.lower()
                if ext in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.yml', '.yaml', '.csv']:
                    file_type = 'text/plain'
                elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
                    file_type = 'image/jpeg'
                elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.wmv']:
                    file_type = 'video/mp4'
                elif ext in ['.mp3', '.wav', '.flac', '.ogg']:
                    file_type = 'audio/mpeg'
                elif ext == '.pdf':
                    file_type = 'application/pdf'
                else:
                    file_type = 'application/octet-stream'
            
            # Read actual content for text files
            if file_type.startswith('text/') or file_type in ['application/json', 'application/xml']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(max_chars)
                    return f"File type: {file_type}\nActual content:\n{content}"
            
            # Describe binary files by type and size
            elif file_type.startswith('image/'):
                return f"Image file: {file_type}, Size: {file_path.stat().st_size} bytes"
            elif file_type.startswith('video/'):
                return f"Video file: {file_type}, Size: {file_path.stat().st_size} bytes"
            elif file_type.startswith('audio/'):
                return f"Audio file: {file_type}, Size: {file_path.stat().st_size} bytes"
            elif file_type == 'application/pdf':
                return f"PDF document, Size: {file_path.stat().st_size} bytes"
            else:
                return f"Binary file: {file_type}, Size: {file_path.stat().st_size} bytes"
                
        except Exception as e:
            return f"Error reading file content: {e}"
    
    def analyze_content_for_category(self, file_path: Path) -> Dict:
        """Analyze actual file content to suggest category - not based on extension"""
        content_info = self.extract_file_content(file_path)
        
        prompt = f"""
        Analyze this file's ACTUAL CONTENT and suggest the best category for organization.
        
        File name: {file_path.name}
        File location: {file_path}
        {content_info}
        
        Based on the ACTUAL CONTENT (not filename or extension), determine:
        1. Main category (e.g., Work Documents, Personal Files, Code Projects, Media, etc.)
        2. Subcategory if appropriate (e.g., Financial Reports, Python Scripts, Family Photos)
        3. Confidence score (0-100) based on content analysis
        4. Brief explanation of why this categorization fits the content
        
        Respond in JSON format only:
        {{"category": "main_category", "subcategory": "sub_category", "confidence": 85, "reason": "explanation based on content analysis"}}
        """
        
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                options={"temperature": 0.3}
            )
            
            response_text = response['message']['content']
            
            # Extract JSON from AI response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "category": "Uncategorized",
                    "subcategory": "Analysis Failed",
                    "confidence": 0,
                    "reason": "Could not parse AI response"
                }
                
        except Exception as e:
            console.print(f"[red]Error analyzing content of {file_path}: {e}")
            return {
                "category": "Uncategorized", 
                "subcategory": "Error",
                "confidence": 0,
                "reason": f"Analysis failed: {e}"
            }


class IntelligentFileOrganizer:
    """Main organizer that implements VG requirements"""
    
    def __init__(self, target_directory: Path, interactive_mode: bool = True):
        self.target_directory = Path(target_directory)
        self.interactive_mode = interactive_mode
        self.analyzer = FileContentAnalyzer()
        self.analysis_results = {}
        
    def discover_all_files(self) -> List[Path]:
        """Discover ALL files in folder structure - requirement: process all files"""
        discovered_files = []
        
        for root, dirs, filenames in os.walk(self.target_directory):
            # Skip hidden directories and system directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules']]
            
            for filename in filenames:
                # Skip hidden files and system files
                if filename.startswith('.') or filename in ['Thumbs.db', 'Desktop.ini']:
                    continue
                    
                file_path = Path(root) / filename
                discovered_files.append(file_path)
                    
        return discovered_files
    
    def analyze_all_content(self, files: List[Path]) -> Dict[Path, Dict]:
        """Analyze actual content of all discovered files"""
        analysis_results = {}
        
        console.print("[blue]Analyzing file content with local AI...[/blue]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Content analysis in progress...", total=len(files))
            
            for file_path in files:
                progress.update(task, description=f"Analyzing: {file_path.name}")
                analysis_results[file_path] = self.analyzer.analyze_content_for_category(file_path)
                progress.advance(task)
                
        return analysis_results
    
    def generate_organization_proposal(self, analysis_results: Dict[Path, Dict]) -> Dict[str, List[Tuple[Path, str]]]:
        """Generate organization proposal based on content analysis"""
        organization_proposal = {}
        
        for file_path, analysis in analysis_results.items():
            category = analysis.get('category', 'Uncategorized')
            subcategory = analysis.get('subcategory', '')
            
            # Create hierarchical folder structure
            if subcategory and subcategory not in ['Unknown', 'Analysis Failed', 'Error']:
                folder_structure = f"{category}/{subcategory}"
            else:
                folder_structure = category
                
            if folder_structure not in organization_proposal:
                organization_proposal[folder_structure] = []
                
            organization_proposal[folder_structure].append((file_path, analysis.get('reason', '')))
            
        return organization_proposal
    
    def display_analysis_summary(self, analysis_results: Dict[Path, Dict]):
        """Display content analysis results"""
        table = Table(title="Content Analysis Results")
        table.add_column("File", style="cyan", min_width=20)
        table.add_column("Detected Category", style="green", min_width=15)
        table.add_column("Subcategory", style="blue", min_width=15)
        table.add_column("Confidence", style="yellow", min_width=10)
        table.add_column("Content-Based Reasoning", style="white", min_width=30)
        
        for file_path, analysis in analysis_results.items():
            reason = analysis.get('reason', 'No explanation provided')
            truncated_reason = reason[:47] + "..." if len(reason) > 50 else reason
            
            table.add_row(
                str(file_path.relative_to(self.target_directory)),
                analysis.get('category', 'Unknown'),
                analysis.get('subcategory', 'Unknown'),
                f"{analysis.get('confidence', 0)}%",
                truncated_reason
            )
            
        console.print(table)
    
    def display_organization_proposal(self, proposal: Dict[str, List[Tuple[Path, str]]]):
        """Display the proposed organization structure"""
        console.print("\n[blue]Proposed Organization Structure:[/blue]")
        console.print("Based on content analysis, the following organization is suggested:\n")
        
        for folder_name, files in proposal.items():
            console.print(f"  [bold blue]{folder_name}[/bold blue]: {len(files)} files")
            
        console.print(f"\nTotal categories proposed: {len(proposal)}")
        console.print(f"Total files to organize: {sum(len(files) for files in proposal.values())}")
    
    def request_sorting_policy_approval(self, proposal: Dict[str, List[Tuple[Path, str]]]) -> bool:
        """Request user approval of the sorting policy"""
        console.print("\n[yellow]SORTING POLICY APPROVAL REQUIRED[/yellow]")
        console.print("The AI has analyzed file content and proposes the above organization structure.")
        console.print("This will create new folders and move files based on their actual content.")
        
        return Confirm.ask("\nDo you approve this sorting policy and want to proceed with organization?")
    
    def execute_organization_plan(self, proposal: Dict[str, List[Tuple[Path, str]]], dry_run: bool = False):
        """Execute the approved organization plan"""
        organized_directory = self.target_directory / "organized_by_content"
        
        if not dry_run:
            organized_directory.mkdir(exist_ok=True)
        
        console.print("\n[green]Executing organization plan...[/green]")
        
        for folder_name, files in proposal.items():
            target_folder = organized_directory / folder_name
            
            console.print(f"\n[bold blue]Organizing: {folder_name}[/bold blue]")
            console.print(f"Files to process: {len(files)}")
            
            if not dry_run:
                target_folder.mkdir(parents=True, exist_ok=True)
                
                for file_path, reason in files:
                    try:
                        target_path = target_folder / file_path.name
                        
                        # Handle naming conflicts
                        counter = 1
                        while target_path.exists():
                            stem = file_path.stem
                            suffix = file_path.suffix
                            target_path = target_folder / f"{stem}_{counter}{suffix}"
                            counter += 1
                        
                        shutil.move(str(file_path), str(target_path))
                        console.print(f"  [green]Moved[/green] {file_path.name} -> {folder_name}/")
                        
                    except Exception as e:
                        console.print(f"  [red]Error moving {file_path.name}: {e}[/red]")
            else:
                for file_path, reason in files:
                    console.print(f"  [dry-run] {file_path.name} -> {folder_name}/")


@click.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--headless', is_flag=True, default=False, 
              help='Headless mode: no user interaction, automatic execution')
@click.option('--interactive', is_flag=True, default=True,
              help='Interactive mode: user approval required (default)')
@click.option('--dry-run', is_flag=True, help='Show what would be done without moving files')
@click.option('--model', default='llama3.2:1b', help='Local AI model to use for content analysis')
def main(directory, headless, interactive, dry_run, model):
    """
    Intelligent File Organizer
    
    Analyzes file content using local AI and organizes files into intelligent categories.
    
    DIRECTORY: Target directory to organize
    """
    
    # Ensure only one mode is selected
    if headless and interactive:
        console.print("[red]Error: Cannot use both --headless and --interactive modes[/red]")
        sys.exit(1)
    
    # Default to interactive if neither specified
    mode = not headless
    
    console.print("[bold green]Intelligent File Organizer - Content-Based Sorting[/bold green]")
    console.print(f"Target directory: {directory}")
    console.print(f"Mode: {'Interactive (user approval required)' if mode else 'Headless (automatic execution)'}")
    console.print(f"Local AI model: {model}")
    
    if dry_run:
        console.print("[yellow]DRY RUN MODE - No files will be moved[/yellow]")
    
    console.print("\n[blue]Features:[/blue]")
    console.print("- Content-based analysis (not just file extensions)")
    console.print("- Dynamic category discovery using AI")
    console.print("- Local AI processing for privacy")
    console.print("- Smart organization with user approval")
    
    # Initialize organizer
    organizer = IntelligentFileOrganizer(Path(directory), interactive_mode=mode)
    organizer.analyzer.model_name = model
    
    # Verify local AI connection
    console.print("\n[blue]Verifying local AI connection...[/blue]")
    if not organizer.analyzer.verify_local_ai_connection():
        console.print("[red]FAILED: Cannot connect to local AI (Ollama)[/red]")
        console.print("[blue]Note: Local AI must be running[/blue]")
        console.print("[blue]Solution: Start Ollama with 'ollama serve'[/blue]")
        sys.exit(1)
    
    console.print("[green]Local AI connection verified[/green]")
    
    # Discover all files in folder structure
    console.print("\n[blue]Discovering all files in folder structure...[/blue]")
    all_files = organizer.discover_all_files()
    console.print(f"Found {len(all_files)} files to analyze")
    
    if not all_files:
        console.print("[yellow]No files found to organize[/yellow]")
        return
    
    # Analyze actual content for intelligent categorization
    console.print(f"\n[blue]Analyzing actual content of {len(all_files)} files...[/blue]")
    console.print("[yellow]Note: Categories are unknown at start - AI will determine organization[/yellow]")
    
    analysis_results = organizer.analyze_all_content(all_files)
    
    # Display content analysis results
    console.print("\n[green]Content Analysis Complete![/green]")
    organizer.display_analysis_summary(analysis_results)
    
    # Generate organization proposal based on content analysis
    console.print("\n[blue]Generating organization proposal based on content...[/blue]")
    organization_proposal = organizer.generate_organization_proposal(analysis_results)
    
    # Display the proposed organization
    organizer.display_organization_proposal(organization_proposal)
    
    # Interactive mode - user approval of sorting policy
    proceed = True
    if mode:  # Interactive mode
        proceed = organizer.request_sorting_policy_approval(organization_proposal)
        if not proceed:
            console.print("[yellow]Organization cancelled by user[/yellow]")
            return
    else:  # Headless mode
        console.print("\n[blue]Headless mode: Proceeding automatically with organization[/blue]")
    
    # Execute the organization plan
    console.print("\n[green]Executing content-based organization...[/green]")
    organizer.execute_organization_plan(organization_proposal, dry_run=dry_run)
    
    # Summary
    if not dry_run:
        console.print("\n[bold green]Organization Complete![/bold green]")
        console.print(f"Files organized by content in: {Path(directory) / 'organized_by_content'}")
        console.print(f"Categories created: {len(organization_proposal)}")
        console.print(f"Files organized: {sum(len(files) for files in organization_proposal.values())}")
    else:
        console.print("\n[yellow]Dry run complete - no files were moved[/yellow]")
        console.print("Remove --dry-run flag to execute the organization")


if __name__ == "__main__":
    main()