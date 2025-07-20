#!/usr/bin/env python3
import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import anthropic
from datetime import datetime
import argparse

class ObsidianVaultOrganizer:
    def __init__(self, vault_path: str, api_key: str):
        """
        Initialize the Obsidian Vault Organizer.
        
        Args:
            vault_path: Path to the Obsidian vault directory
            api_key: Anthropic API key
        """
        self.vault_path = Path(vault_path)
        self.api_key = api_key
        self.client = anthropic.Anthropic(api_key=api_key)
        self.file_index = []
        
    def index_vault(self) -> List[Dict[str, str]]:
        """
        Index all files in the vault, collecting folder and filename information.
        
        Returns:
            List of dictionaries containing file information
        """
        print("Indexing vault files...")
        
        for root, dirs, files in os.walk(self.vault_path):
            # Skip hidden directories (like .obsidian)
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                # Skip hidden files and non-markdown files
                if file.startswith('.') or not file.endswith('.md'):
                    continue
                
                full_path = Path(root) / file
                relative_path = full_path.relative_to(self.vault_path)
                
                file_info = {
                    'filename': file,
                    'current_folder': str(relative_path.parent),
                    'full_relative_path': str(relative_path),
                    'size': os.path.getsize(full_path)
                }
                
                self.file_index.append(file_info)
        
        print(f"Indexed {len(self.file_index)} files")
        return self.file_index
    
    def get_organization_suggestions(self) -> Dict:
        """
        Send the file index to Claude and get organization suggestions.
        
        Returns:
            Dictionary with the new organization structure
        """
        print("Getting organization suggestions from Claude...")
        
        # Prepare the prompt
        prompt = f"""I have an Obsidian vault with the following file structure. Please analyze the filenames and current folder structure, then suggest a better organization. 

Current file structure:
{json.dumps(self.file_index, indent=2)}

Please respond with a JSON structure that maps each file to its new location. The format should be:
{{
    "organization_plan": {{
        "current_file_path": "new_folder_path",
        ...
    }},
    "folder_descriptions": {{
        "folder_name": "description of what goes in this folder",
        ...
    }}
}}

Consider:
1. Group files by topic, type, or purpose based on their names
2. Create a logical hierarchy that makes files easy to find
3. Use clear, descriptive folder names
4. Don't create too many levels of nesting (max 3 levels deep)
5. Keep the existing structure if it already makes sense

Only return valid JSON, no other text."""
        
        try:
            message = self.client.messages.create(
                model="claude-opus-4-20250514",
                max_tokens=4000,
                temperature=0,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse the response
            response_text = message.content[0].text
            
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                organization_data = json.loads(json_match.group())
                return organization_data
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            print(f"Error getting suggestions from Claude: {e}")
            return None
    
    def create_backup(self):
        """Create a backup of the current vault structure."""
        backup_dir = self.vault_path.parent / f"obsidian_vault_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"Creating backup at {backup_dir}...")
        shutil.copytree(self.vault_path, backup_dir, ignore=shutil.ignore_patterns('.obsidian', '.git'))
        print("Backup created successfully")
        return backup_dir
    
    def reorganize_vault(self, organization_plan: Dict):
        """
        Reorganize the vault based on Claude's suggestions.
        
        Args:
            organization_plan: Dictionary mapping current paths to new paths
        """
        print("Reorganizing vault...")
        
        # Create all new directories first
        new_dirs = set()
        for new_path in organization_plan['organization_plan'].values():
            new_dir = Path(new_path)
            if new_dir != Path('.'):
                new_dirs.add(new_dir)
        
        for new_dir in new_dirs:
            full_dir_path = self.vault_path / new_dir
            full_dir_path.mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {new_dir}")
        
        # Move files
        moved_count = 0
        for file_info in self.file_index:
            current_path = file_info['full_relative_path']
            
            if current_path in organization_plan['organization_plan']:
                new_folder = organization_plan['organization_plan'][current_path]
                new_path = Path(new_folder) / file_info['filename']
                
                current_full_path = self.vault_path / current_path
                new_full_path = self.vault_path / new_path
                
                if current_full_path != new_full_path:
                    try:
                        # Create parent directory if it doesn't exist
                        new_full_path.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Move the file
                        shutil.move(str(current_full_path), str(new_full_path))
                        print(f"Moved: {current_path} -> {new_path}")
                        moved_count += 1
                    except Exception as e:
                        print(f"Error moving {current_path}: {e}")
        
        print(f"Moved {moved_count} files")
        
        # Clean up empty directories
        self.cleanup_empty_dirs()
        
        # Save organization report
        self.save_organization_report(organization_plan)
    
    def cleanup_empty_dirs(self):
        """Remove empty directories from the vault."""
        print("Cleaning up empty directories...")
        
        for root, dirs, files in os.walk(self.vault_path, topdown=False):
            # Skip hidden directories
            if any(part.startswith('.') for part in Path(root).parts):
                continue
                
            if not dirs and not files:
                try:
                    os.rmdir(root)
                    print(f"Removed empty directory: {Path(root).relative_to(self.vault_path)}")
                except:
                    pass
    
    def save_organization_report(self, organization_plan: Dict):
        """Save a report of the reorganization."""
        report_path = self.vault_path / "_organization_report.md"
        
        with open(report_path, 'w') as f:
            f.write("# Vault Organization Report\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            if 'folder_descriptions' in organization_plan:
                f.write("## Folder Structure\n\n")
                for folder, description in organization_plan['folder_descriptions'].items():
                    f.write(f"### {folder}\n")
                    f.write(f"{description}\n\n")
            
            f.write("## File Movements\n\n")
            for current, new in organization_plan['organization_plan'].items():
                if Path(current).parent != Path(new):
                    f.write(f"- `{current}` → `{new}/{Path(current).name}`\n")
        
        print(f"Organization report saved to {report_path}")
    
    def run(self, create_backup: bool = True):
        """
        Run the complete vault organization process.
        
        Args:
            create_backup: Whether to create a backup before reorganizing
        """
        print(f"Starting Obsidian Vault Organization for: {self.vault_path}\n")
        
        # Step 1: Index the vault
        self.index_vault()
        
        if not self.file_index:
            print("No markdown files found in the vault.")
            return
        
        # Step 2: Create backup if requested
        if create_backup:
            backup_path = self.create_backup()
            print(f"Backup created at: {backup_path}\n")
        
        # Step 3: Get organization suggestions from Claude
        organization_plan = self.get_organization_suggestions()
        
        if not organization_plan:
            print("Failed to get organization suggestions.")
            return
        
        # Step 4: Show the plan and ask for confirmation
        print("\nProposed organization plan:")
        if 'folder_descriptions' in organization_plan:
            for folder, description in organization_plan['folder_descriptions'].items():
                print(f"\n{folder}: {description}")
        
        response = input("\nDo you want to proceed with the reorganization? (yes/no): ")
        
        if response.lower() in ['yes', 'y']:
            # Step 5: Reorganize the vault
            self.reorganize_vault(organization_plan)
            print("\nVault reorganization complete!")
        else:
            print("Reorganization cancelled.")

def main():
    parser = argparse.ArgumentParser(description="Organize your Obsidian vault using Claude AI")
    parser.add_argument("vault_path", help="Path to your Obsidian vault")
    parser.add_argument("--api-key", required=True, help="Your Anthropic API key")
    parser.add_argument("--no-backup", action="store_true", help="Skip creating a backup")
    
    args = parser.parse_args()
    
    # Validate vault path
    vault_path = Path(args.vault_path)
    if not vault_path.exists() or not vault_path.is_dir():
        print(f"Error: {vault_path} is not a valid directory")
        return
    
    # Create and run organizer
    organizer = ObsidianVaultOrganizer(str(vault_path), args.api_key)
    organizer.run(create_backup=not args.no_backup)

if __name__ == "__main__":
    main()