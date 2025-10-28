#!/usr/bin/env python3
"""
Example script demonstrating the Face Repository system.

This script shows how to use the repository commands in a typical workflow.
"""

# Example workflow demonstration
print("=" * 60)
print("FaceFusion Face Repository - Example Workflow")
print("=" * 60)
print()

print("Step 1: Initialize Repository")
print("-" * 60)
print("Command: python facefusion.py repo-init")
print()

print("Step 2: Add Faces to Repository")
print("-" * 60)
print("Command: python facefusion.py repo-add --person \"John\" -s john.jpg")
print()

print("Step 3: List Repository")
print("-" * 60)
print("Command: python facefusion.py repo-list")
print()

print("Step 4: Execute Face Swapping")
print("-" * 60)
print("Command: python facefusion.py repo-execute --person \"John\" -t video.mp4 -o output.mp4")
print()

print("For more information, see facefusion_repository/README.md")
