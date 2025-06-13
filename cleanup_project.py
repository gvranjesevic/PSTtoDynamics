#!/usr/bin/env python3
"""
Project Cleanup and Organization Script
=======================================

Organizes the PST-to-Dynamics project structure by moving files to appropriate
directories and cleaning up development artifacts.
"""

import os
import shutil
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class ProjectCleaner:
    """Handles project cleanup and organization."""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.moved_files = []
        self.deleted_files = []
        self.created_dirs = []
        
    def organize_project(self) -> bool:
        """Main method to organize the entire project."""
        print("🧹 Starting project cleanup and organization...")
        print(f"📁 Project root: {self.project_root}")
        
        try:
            self._create_directory_structure()
            self._organize_test_files()
            self._organize_development_files()
            self._organize_documentation()
            self._organize_phase_files()
            self._clean_up_artifacts()
            self._update_gitignore()
            
            self._print_summary()
            return True
            
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            return False
    
    def _create_directory_structure(self):
        """Create the standard directory structure."""
        directories = [
            "tests",
            "docs",
            "development",
            "development/phases",
            "development/archive",
            "development/scripts",
            "gui/resources",
            "gui/themes",
            "sync",
            "Phase3_Analytics",
            "ml_models",
            "logs",
            "exports"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                self.created_dirs.append(str(dir_path))
                print(f"📁 Created directory: {directory}")
    
    def _organize_test_files(self):
        """Move all test files to the tests directory."""
        test_patterns = [
            "test_*.py",
            "*_test.py",
            "debug_*.py"
        ]
        
        test_files = []
        for pattern in test_patterns:
            test_files.extend(self.project_root.glob(pattern))
        
        tests_dir = self.project_root / "tests"
        
        for test_file in test_files:
            if test_file.parent == tests_dir:
                continue  # Already in tests directory
                
            new_path = tests_dir / test_file.name
            if not new_path.exists():
                shutil.move(str(test_file), str(new_path))
                self.moved_files.append((str(test_file), str(new_path)))
                print(f"📄 Moved test file: {test_file.name} → tests/")
    
    def _organize_development_files(self):
        """Move development files to development directory."""
        dev_patterns = [
            "phase*.py",
            "*_summary.py",
            "*_planning.md",
            "*_completion*.md",
            "*_implementation*.md",
            "*_guide.md",
            "generate_*.py",
            "cleanup_*.py",
            "database_init.py"
        ]
        
        dev_files = []
        for pattern in dev_patterns:
            dev_files.extend(self.project_root.glob(pattern))
        
        # Separate phase files from other development files
        phase_files = [f for f in dev_files if f.name.lower().startswith('phase')]
        other_dev_files = [f for f in dev_files if not f.name.lower().startswith('phase')]
        
        # Move phase files
        phases_dir = self.project_root / "development" / "phases"
        for phase_file in phase_files:
            if phase_file.parent == phases_dir:
                continue
            
            new_path = phases_dir / phase_file.name
            if not new_path.exists():
                shutil.move(str(phase_file), str(new_path))
                self.moved_files.append((str(phase_file), str(new_path)))
                print(f"📄 Moved phase file: {phase_file.name} → development/phases/")
        
        # Move other development files
        scripts_dir = self.project_root / "development" / "scripts"
        for dev_file in other_dev_files:
            if dev_file.parent in [scripts_dir, phases_dir]:
                continue
            
            new_path = scripts_dir / dev_file.name
            if not new_path.exists():
                shutil.move(str(dev_file), str(new_path))
                self.moved_files.append((str(dev_file), str(new_path)))
                print(f"📄 Moved script: {dev_file.name} → development/scripts/")
    
    def _organize_documentation(self):
        """Move documentation files to docs directory."""
        doc_patterns = [
            "*.md",
            "USER_MANUAL.*",
            "QA_CHECKLIST.*",
            "README.*"
        ]
        
        docs_dir = self.project_root / "docs"
        
        for pattern in doc_patterns:
            for doc_file in self.project_root.glob(pattern):
                # Skip if already in docs or development directories
                if doc_file.parent in [docs_dir, self.project_root / "development"]:
                    continue
                
                # Keep README.md in root
                if doc_file.name == "README.md":
                    continue
                
                new_path = docs_dir / doc_file.name
                if not new_path.exists():
                    shutil.move(str(doc_file), str(new_path))
                    self.moved_files.append((str(doc_file), str(new_path)))
                    print(f"📄 Moved documentation: {doc_file.name} → docs/")
    
    def _organize_phase_files(self):
        """Move phase-related files to development/phases."""
        # Already handled in _organize_development_files
        pass
    
    def _clean_up_artifacts(self):
        """Clean up build artifacts and temporary files."""
        artifacts_to_clean = [
            "__pycache__",
            "*.pyc",
            "*.pyo",
            "*.pyd",
            ".pytest_cache",
            "build",
            "*.egg-info"
        ]
        
        # Clean pycache directories
        for pycache_dir in self.project_root.rglob("__pycache__"):
            if pycache_dir.is_dir():
                shutil.rmtree(pycache_dir)
                self.deleted_files.append(str(pycache_dir))
                print(f"🗑️ Removed: {pycache_dir.relative_to(self.project_root)}")
        
        # Clean .pyc files
        for pyc_file in self.project_root.rglob("*.pyc"):
            pyc_file.unlink()
            self.deleted_files.append(str(pyc_file))
        
        # Clean build directories (except dist for distribution)
        for build_dir in ["build"]:
            build_path = self.project_root / build_dir
            if build_path.exists() and build_path.is_dir():
                # Keep if it contains important files
                important_files = list(build_path.rglob("*.exe")) + list(build_path.rglob("*.msi"))
                if not important_files:
                    shutil.rmtree(build_path)
                    self.deleted_files.append(str(build_path))
                    print(f"🗑️ Removed build directory: {build_dir}")
    
    def _update_gitignore(self):
        """Update .gitignore with common Python and project-specific patterns."""
        gitignore_path = self.project_root / ".gitignore"
        
        # Standard patterns to add
        patterns_to_add = [
            "# Python artifacts",
            "__pycache__/",
            "*.py[cod]",
            "*$py.class",
            "*.so",
            ".Python",
            "build/",
            "develop-eggs/",
            "downloads/",
            "eggs/",
            ".eggs/",
            "lib/",
            "lib64/",
            "parts/",
            "sdist/",
            "var/",
            "wheels/",
            "*.egg-info/",
            ".installed.cfg",
            "*.egg",
            "",
            "# Testing",
            ".pytest_cache/",
            ".coverage",
            "htmlcov/",
            "",
            "# Environment",
            ".env",
            ".venv",
            "venv/",
            "ENV/",
            "",
            "# IDE",
            ".vscode/",
            ".idea/",
            "*.swp",
            "*.swo",
            "*~",
            "",
            "# Project specific",
            "*.db",
            "*.db-journal",
            "logs/",
            "exports/",
            "temp/",
            "*.pst",
            "ml_models/*.pkl",
            "ml_models/*.joblib"
        ]
        
        # Read existing gitignore
        existing_patterns = set()
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                existing_patterns = set(line.strip() for line in f if line.strip() and not line.startswith('#'))
        
        # Add new patterns
        new_patterns = []
        for pattern in patterns_to_add:
            if pattern and not pattern.startswith('#') and pattern not in existing_patterns:
                new_patterns.append(pattern)
        
        if new_patterns:
            with open(gitignore_path, 'a', encoding='utf-8') as f:
                f.write('\n# Added by cleanup script\n')
                for pattern in patterns_to_add:
                    f.write(f'{pattern}\n')
            print(f"📝 Updated .gitignore with {len(new_patterns)} new patterns")
    
    def _print_summary(self):
        """Print a summary of all cleanup actions."""
        print("\n" + "="*50)
        print("🎉 Project cleanup completed!")
        print("="*50)
        
        if self.created_dirs:
            print(f"\n📁 Created {len(self.created_dirs)} directories:")
            for directory in self.created_dirs[-5:]:  # Show last 5
                print(f"   • {directory}")
            if len(self.created_dirs) > 5:
                print(f"   ... and {len(self.created_dirs) - 5} more")
        
        if self.moved_files:
            print(f"\n📄 Moved {len(self.moved_files)} files:")
            for old_path, new_path in self.moved_files[-5:]:  # Show last 5
                old_name = Path(old_path).name
                new_dir = Path(new_path).parent.name
                print(f"   • {old_name} → {new_dir}/")
            if len(self.moved_files) > 5:
                print(f"   ... and {len(self.moved_files) - 5} more")
        
        if self.deleted_files:
            print(f"\n🗑️ Cleaned up {len(self.deleted_files)} artifacts")
        
        print(f"\n✨ Project is now organized and clean!")
        print("\nRecommended next steps:")
        print("1. Review the moved files in development/ directory")
        print("2. Update import statements if needed")
        print("3. Run tests to ensure everything still works")
        print("4. Commit the organized structure to git")

def main():
    """Main function to run project cleanup."""
    print("🧹 PST-to-Dynamics Project Cleanup")
    print("=" * 40)
    
    cleaner = ProjectCleaner()
    
    # Ask for confirmation
    response = input("This will reorganize files in the project. Continue? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print("❌ Cleanup cancelled.")
        return False
    
    success = cleaner.organize_project()
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1) 