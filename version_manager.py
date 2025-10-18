#!/usr/bin/env python3
"""
Version Management Script for 360 Magicians

This script automates version updates and changelog management.
It supports semantic versioning (MAJOR.MINOR.PATCH) and integrates with Git tags.

Usage:
    python version_manager.py --bump [major|minor|patch] --message "Release message"
    python version_manager.py --get-version
    python version_manager.py --create-tag
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path


class VersionManager:
    """Manages version updates and changelog entries."""
    
    def __init__(self, repo_root=None):
        """Initialize the version manager.
        
        Args:
            repo_root: Path to the repository root. Defaults to current directory.
        """
        self.repo_root = Path(repo_root) if repo_root else Path(__file__).parent
        self.version_file = self.repo_root / "version.txt"
        self.changelog_file = self.repo_root / "CHANGELOG.md"
    
    def get_current_version(self):
        """Read the current version from version.txt.
        
        Returns:
            str: Current version string (e.g., "0.1.0")
        """
        if not self.version_file.exists():
            return "0.0.0"
        return self.version_file.read_text().strip()
    
    def parse_version(self, version_str):
        """Parse a version string into major, minor, patch components.
        
        Args:
            version_str: Version string (e.g., "1.2.3")
            
        Returns:
            tuple: (major, minor, patch) as integers
        """
        match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', version_str)
        if not match:
            raise ValueError(f"Invalid version format: {version_str}")
        return tuple(map(int, match.groups()))
    
    def bump_version(self, bump_type):
        """Increment the version based on the bump type.
        
        Args:
            bump_type: One of 'major', 'minor', or 'patch'
            
        Returns:
            str: New version string
        """
        current = self.get_current_version()
        major, minor, patch = self.parse_version(current)
        
        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1
        else:
            raise ValueError(f"Invalid bump type: {bump_type}. Use 'major', 'minor', or 'patch'")
        
        new_version = f"{major}.{minor}.{patch}"
        return new_version
    
    def update_version_file(self, new_version):
        """Write the new version to version.txt.
        
        Args:
            new_version: Version string to write
        """
        self.version_file.write_text(new_version + "\n")
        print(f"Updated version.txt to {new_version}")
    
    def update_changelog(self, version, message):
        """Update CHANGELOG.md with a new version entry.
        
        Args:
            version: Version string for the new release
            message: Release message describing the changes
        """
        if not self.changelog_file.exists():
            print("Warning: CHANGELOG.md not found. Skipping changelog update.")
            return
        
        content = self.changelog_file.read_text()
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Create the new changelog entry
        new_entry = f"\n## [{version}] - {today}\n\n{message}\n"
        
        # Insert after the [Unreleased] section
        unreleased_pattern = r'(## \[Unreleased\].*?)(\n## \[|$)'
        
        def replace_func(match):
            return match.group(1) + new_entry + match.group(2)
        
        updated_content = re.sub(unreleased_pattern, replace_func, content, flags=re.DOTALL)
        
        self.changelog_file.write_text(updated_content)
        print(f"Updated CHANGELOG.md with version {version}")
    
    def create_git_tag(self, version, message=""):
        """Create a Git tag for the version.
        
        Args:
            version: Version string for the tag
            message: Optional tag message
        """
        import subprocess
        
        tag_name = f"v{version}"
        tag_message = message or f"Release version {version}"
        
        try:
            # Create annotated tag
            subprocess.run(
                ["git", "tag", "-a", tag_name, "-m", tag_message],
                check=True,
                cwd=self.repo_root
            )
            print(f"Created Git tag: {tag_name}")
            print("Note: Push the tag with: git push origin --tags")
        except subprocess.CalledProcessError as e:
            print(f"Error creating Git tag: {e}")
            sys.exit(1)
        except FileNotFoundError:
            print("Git not found. Skipping tag creation.")


def main():
    """Main entry point for the version manager CLI."""
    parser = argparse.ArgumentParser(
        description="Manage versions and changelog for 360 Magicians"
    )
    parser.add_argument(
        "--bump",
        choices=["major", "minor", "patch"],
        help="Bump version (major, minor, or patch)"
    )
    parser.add_argument(
        "--message",
        help="Release message for changelog"
    )
    parser.add_argument(
        "--get-version",
        action="store_true",
        help="Display the current version"
    )
    parser.add_argument(
        "--create-tag",
        action="store_true",
        help="Create a Git tag for the current version"
    )
    
    args = parser.parse_args()
    manager = VersionManager()
    
    if args.get_version:
        print(manager.get_current_version())
        return
    
    if args.create_tag:
        current_version = manager.get_current_version()
        manager.create_git_tag(current_version, args.message or "")
        return
    
    if args.bump:
        if not args.message:
            print("Error: --message is required when bumping version")
            sys.exit(1)
        
        new_version = manager.bump_version(args.bump)
        manager.update_version_file(new_version)
        manager.update_changelog(new_version, args.message)
        
        print(f"\nVersion bumped from {manager.get_current_version()} to {new_version}")
        print("Next steps:")
        print("  1. Review the changes in version.txt and CHANGELOG.md")
        print("  2. Commit the changes: git add version.txt CHANGELOG.md && git commit -m 'Bump version to {}'".format(new_version))
        print(f"  3. Create a tag: python version_manager.py --create-tag --message 'Release {new_version}'")
        print("  4. Push changes and tags: git push && git push origin --tags")
        return
    
    parser.print_help()


if __name__ == "__main__":
    main()
