#!/usr/bin/env python3
"""
Cleanup script to remove old migrated files and temporary files.
"""

import os
import shutil
import glob

def main():
    """Clean up old files and directories."""
    
    print("🧹 CLEANUP: Removing old migrated files and temporary files")
    print("=" * 60)
    
    # Directories to remove (migrated to new base architecture)
    old_dirs = [
        "asymptote_questions",      # Migrated to AsymptoteGenerator
        "asymptotic_advanced",      # Migrated to AdvancedAsymptoteGenerator
        "true_false_triangle",      # Migrated to TriangleGenerator
        "base_template"            # Replaced by base/
    ]
    
    # Generated files to remove
    generated_patterns = [
        "*.tex",          # Generated LaTeX files
        "*.aux",          # LaTeX auxiliary files
        "*.log",          # LaTeX log files
        "*.pdf",          # Generated PDF files
        "*.fdb_latexmk",  # LaTeX build files
        "*.fls",          # LaTeX build files
        "*.synctex.gz"    # LaTeX sync files
    ]
    
    # Remove old directories
    for dir_name in old_dirs:
        if os.path.exists(dir_name):
            print(f"🗑️  Removing directory: {dir_name}/")
            shutil.rmtree(dir_name)
            print(f"   ✅ Removed {dir_name}/")
        else:
            print(f"   ⚠️  Directory not found: {dir_name}/")
    
    print()
    
    # Remove generated files
    removed_files = []
    for pattern in generated_patterns:
        files = glob.glob(pattern)
        for file in files:
            if os.path.isfile(file):
                os.remove(file)
                removed_files.append(file)
    
    if removed_files:
        print("🗑️  Removed generated files:")
        for file in removed_files:
            print(f"   ✅ {file}")
    else:
        print("   ℹ️  No generated files to remove")
    
    print()
    
    # Remove __pycache__ directories
    pycache_dirs = []
    for root, dirs, files in os.walk("."):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                pycache_path = os.path.join(root, dir_name)
                pycache_dirs.append(pycache_path)
    
    if pycache_dirs:
        print("🗑️  Removing __pycache__ directories:")
        for pycache_dir in pycache_dirs:
            shutil.rmtree(pycache_dir)
            print(f"   ✅ {pycache_dir}")
    else:
        print("   ℹ️  No __pycache__ directories to remove")
    
    print()
    print("=" * 60)
    print("🎉 CLEANUP COMPLETE!")
    print()
    print("📋 Summary:")
    print(f"   • Removed {len(old_dirs)} old directories")
    print(f"   • Removed {len(removed_files)} generated files")
    print(f"   • Removed {len(pycache_dirs)} __pycache__ directories")
    print()
    print("🏗️  Repository is now clean and ready for next phase!")

if __name__ == "__main__":
    main()
