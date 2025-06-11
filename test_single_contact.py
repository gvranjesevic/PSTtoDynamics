#!/usr/bin/env python3
"""Test single contact timeline restoration"""

from timeline_restoration_system import TimelineRestorationSystem

# Test with just 1 contact
system = TimelineRestorationSystem(
    'gvranjesevic@dynamique.com', 
    '#SanDiegoChicago77', 
    r'C:\GitHub-Repos\gvranjesevic@dynamique.com\PSTtoDynamics\PST\gvranjesevic@dynamique.com.001.pst'
)

# Run with max 1 contact for testing
success = system.run_timeline_restoration(max_contacts=1)
print(f"\nTest result: {'✅ SUCCESS' if success else '❌ FAILED'}") 