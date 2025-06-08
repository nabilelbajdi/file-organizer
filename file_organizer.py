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
import json
import shutil
import click
import ollama
from pathlib import Path
from typing import List, Dict, Tuple


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
    
    def extract_file_content(self, file_path: Path, max_chars: int = 2000) -> str:
        """Extract file content for AI analysis - actual content, not just extension"""
        try:
            # Read actual content for text files
            ext = file_path.suffix.lower()
            if ext in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.yml', '.yaml', '.csv']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(max_chars)
                    return f"File type: {ext}\nActual content:\n{content}"
            else:
                # Describe binary files by type and size
                return f"Binary file: {ext}, Size: {file_path.stat().st_size} bytes"
        except Exception as e:
            return f"Error reading file content: {e}"
    
    def analyze_content_for_category(self, file_path: Path) -> Dict:
        """Analyze actual file content to suggest category - not based on extension"""
        content_info = self.extract_file_content(file_path)
        
        prompt = f"""
        Analyze this file's ACTUAL CONTENT and suggest the best category for organization.
        
        File name: {file_path.name}
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
            print(f"Error analyzing content of {file_path}: {e}")
            return {
                "category": "Uncategorized", 
                "subcategory": "Error",
                "confidence": 0,
                "reason": f"Analysis failed: {e}"
            }


class FileOrganizer:
    """Main organizer class that implements file discovery"""
    
    def __init__(self, target_directory: Path):
        self.target_directory = Path(target_directory)
        self.analyzer = FileContentAnalyzer()
        
    def discover_all_files(self) -> List[Path]:
        """Discover all files in folder structure recursively"""
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
    
    def analyze_all_content(self, files: List[Path]) -> Dict[Path, Dict]:
        """Analyze actual content of all discovered files"""
        analysis_results = {}
        
        print("Analyzing file content with local AI...")
        
        for i, file_path in enumerate(files, 1):
            print(f"  Analyzing ({i}/{len(files)}): {file_path.name}")
            analysis_results[file_path] = self.analyzer.analyze_content_for_category(file_path)
                
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
    
    def display_organization_proposal(self, proposal: Dict[str, List[Tuple[Path, str]]]):
        """Display the proposed organization structure"""
        print("\nProposed Organization Structure:")
        print("Based on content analysis, the following organization is suggested:\n")
        
        for folder_name, files in proposal.items():
            print(f"  {folder_name}: {len(files)} files")
            
        print(f"\nTotal categories proposed: {len(proposal)}")
        print(f"Total files to organize: {sum(len(files) for files in proposal.values())}")
    
    def request_user_approval(self, proposal: Dict[str, List[Tuple[Path, str]]]) -> bool:
        """Request user approval of the organization proposal"""
        print("\n" + "="*60)
        print("ORGANIZATION APPROVAL REQUIRED")
        print("="*60)
        print("The AI has analyzed file content and proposes the above organization structure.")
        print("This will create new folders and move files based on their actual content.")
        
        while True:
            response = input("\nDo you approve this organization and want to proceed? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")
    
    def execute_organization_plan(self, proposal: Dict[str, List[Tuple[Path, str]]], dry_run: bool = False):
        """Execute the approved organization plan"""
        organized_directory = self.target_directory / "organized_by_content"
        
        if not dry_run:
            organized_directory.mkdir(exist_ok=True)
        
        print(f"\n{'='*60}")
        print(f"EXECUTING ORGANIZATION PLAN")
        print(f"{'='*60}")
        
        total_files = sum(len(files) for files in proposal.values())
        processed = 0
        
        for folder_name, files in proposal.items():
            target_folder = organized_directory / folder_name
            
            print(f"\nOrganizing: {folder_name}")
            print(f"  Files to process: {len(files)}")
            
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
                        processed += 1
                        print(f"  Moved: {file_path.name} -> {folder_name}/")
                        
                    except Exception as e:
                        print(f"  Error moving {file_path.name}: {e}")
            else:
                for file_path, reason in files:
                    processed += 1
                    print(f"  [DRY RUN] {file_path.name} -> {folder_name}/")
        
        # Summary
        if not dry_run:
            print(f"\nOrganization Complete!")
            print(f"Files organized: {processed}/{total_files}")
            print(f"Categories created: {len(proposal)}")
            print(f"Files organized in: {organized_directory}")
        else:
            print(f"\nDry run complete - no files were moved")
            print(f"Would organize: {processed} files into {len(proposal)} categories")
            print("Remove --dry-run flag to execute the organization")


@click.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--headless', is_flag=True, default=False, 
              help='Headless mode: no user interaction, automatic execution')
@click.option('--dry-run', is_flag=True, help='Show what would be done without moving files')
def main(directory, headless, dry_run):
    """
    Intelligent File Organizer
    
    Analyzes file content using local AI and organizes files into intelligent categories.
    
    DIRECTORY: Target directory to organize
    """
    print("Intelligent File Organizer - Content-Based Sorting")
    print(f"Target directory: {directory}")
    print(f"Mode: {'Headless (automatic execution)' if headless else 'Interactive (user approval required)'}")
    
    if dry_run:
        print("DRY RUN MODE - No files will be moved")
    
    print("\nFeatures:")
    print("- Content-based analysis (not just file extensions)")
    print("- Dynamic category discovery using AI")
    print("- Local AI processing for privacy")
    print("- Smart organization with user approval")
    
    # Initialize organizer
    organizer = FileOrganizer(Path(directory))
    
    # Verify local AI connection
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
        
    # Analyze actual content for intelligent categorization
    print(f"\nAnalyzing actual content of {len(all_files)} files...")
    print("Note: Categories are unknown at start - AI will determine organization")
    
    analysis_results = organizer.analyze_all_content(all_files)
    
    # Display content analysis results
    print("\nContent Analysis Complete!")
    print(f"{'File':<25} {'Category':<18} {'Subcategory':<18} {'Confidence':<12}")
    print("-" * 80)
    
    for file_path, analysis in analysis_results.items():
        rel_path = str(file_path.relative_to(organizer.target_directory))
        rel_path = rel_path[:22] + "..." if len(rel_path) > 25 else rel_path
        category = analysis.get('category', 'Unknown')[:15]
        subcategory = analysis.get('subcategory', 'Unknown')[:15] 
        confidence = f"{analysis.get('confidence', 0)}%"
        
        print(f"{rel_path:<25} {category:<18} {subcategory:<18} {confidence:<12}")
    
    # Generate organization proposal based on content analysis
    print("\nGenerating organization proposal based on content...")
    organization_proposal = organizer.generate_organization_proposal(analysis_results)
    
    # Display the proposed organization
    organizer.display_organization_proposal(organization_proposal)
    
    # Interactive mode - user approval required
    proceed = True
    if not headless:  # Interactive mode
        proceed = organizer.request_user_approval(organization_proposal)
        if not proceed:
            print("\nOrganization cancelled by user.")
            print("No files were moved.")
            return
    else:  # Headless mode
        print("\nHeadless mode: Proceeding automatically with organization...")
    
    # Execute the organization plan
    print("\nExecuting intelligent content-based organization...")
    organizer.execute_organization_plan(organization_proposal, dry_run=dry_run)

if __name__ == "__main__":
    main()