#!/usr/bin/env python3
"""
PST Verification Tool
Independent verification tool to count PST messages and validate extraction completeness.
Uses different methods to cross-check message counts.
"""

import os
import sys
import win32com.client
from collections import defaultdict
from tabulate import tabulate


class PSTVerificationTool:
    def __init__(self, pst_file_path):
        """Initialize the verification tool with the path to the PST file."""
        self.pst_file_path = pst_file_path
        self.outlook = None
        self.namespace = None
        self.pst_store = None
        
    def open_pst_file(self):
        """Open the PST file using Outlook COM interface."""
        try:
            if not os.path.exists(self.pst_file_path):
                raise FileNotFoundError(f"PST file not found: {self.pst_file_path}")
            
            print(f"🔍 Starting PST verification...")
            print(f"📁 Opening PST file: {self.pst_file_path}")
            
            # Create Outlook application object
            self.outlook = win32com.client.Dispatch("Outlook.Application")
            self.namespace = self.outlook.GetNamespace("MAPI")
            
            # Add PST file to Outlook
            self.namespace.AddStore(self.pst_file_path)
            
            # Find the PST store
            for store in self.namespace.Stores:
                if store.FilePath.lower() == self.pst_file_path.lower():
                    self.pst_store = store
                    break
            
            if not self.pst_store:
                raise Exception("Could not find PST store after adding")
            
            print(f"✅ PST file opened: {self.pst_store.DisplayName}")
            return True
            
        except Exception as e:
            print(f"❌ Error opening PST file: {str(e)}")
            return False
    
    def close_pst_file(self):
        """Close the PST file and cleanup COM objects."""
        try:
            if self.pst_store:
                self.namespace.RemoveStore(self.pst_store.GetRootFolder())
                print("✅ PST file closed")
                
            if self.outlook:
                self.outlook = None
                self.namespace = None
                self.pst_store = None
                
        except Exception as e:
            print(f"⚠️  Error closing PST file: {str(e)}")
    
    def method1_direct_count(self):
        """Method 1: Direct count using folder.Items.Count."""
        print("\n📊 Method 1: Direct Count (folder.Items.Count)")
        
        folder_counts = {}
        total_count = 0
        
        def count_folder_direct(folder, path=""):
            nonlocal total_count
            current_path = f"{path}/{folder.Name}" if path else folder.Name
            
            try:
                count = folder.Items.Count
                folder_counts[current_path] = count
                total_count += count
                if count > 0:
                    print(f"  📁 {current_path}: {count:,} messages")
            except Exception as e:
                print(f"  ❌ Error counting {current_path}: {str(e)}")
                folder_counts[current_path] = 0
            
            # Process subfolders
            try:
                for i in range(1, folder.Folders.Count + 1):
                    subfolder = folder.Folders.Item(i)
                    count_folder_direct(subfolder, current_path)
            except:
                pass
        
        root_folder = self.pst_store.GetRootFolder()
        count_folder_direct(root_folder)
        
        print(f"📊 Method 1 Total: {total_count:,} messages")
        return total_count, folder_counts
    
    def method2_iterative_count(self):
        """Method 2: Iterative count by actually accessing each message."""
        print("\n📊 Method 2: Iterative Count (accessing each message)")
        
        folder_counts = {}
        total_count = 0
        
        def count_folder_iterative(folder, path=""):
            nonlocal total_count
            current_path = f"{path}/{folder.Name}" if path else folder.Name
            
            try:
                messages = folder.Items
                reported_count = messages.Count
                
                # Actually iterate through messages to verify
                actual_count = 0
                for i in range(1, reported_count + 1):
                    try:
                        message = messages.Item(i)
                        if message:  # Verify message exists
                            actual_count += 1
                    except:
                        pass
                
                folder_counts[current_path] = {
                    'reported': reported_count,
                    'actual': actual_count
                }
                total_count += actual_count
                
                if actual_count > 0:
                    status = "✅" if actual_count == reported_count else "⚠️"
                    print(f"  📁 {current_path}: {actual_count:,} messages {status}")
                    if actual_count != reported_count:
                        print(f"     (Reported: {reported_count}, Actual: {actual_count})")
                        
            except Exception as e:
                print(f"  ❌ Error counting {current_path}: {str(e)}")
                folder_counts[current_path] = {'reported': 0, 'actual': 0}
            
            # Process subfolders
            try:
                for i in range(1, folder.Folders.Count + 1):
                    subfolder = folder.Folders.Item(i)
                    count_folder_iterative(subfolder, current_path)
            except:
                pass
        
        root_folder = self.pst_store.GetRootFolder()
        count_folder_iterative(root_folder)
        
        print(f"📊 Method 2 Total: {total_count:,} messages")
        return total_count, folder_counts
    
    def method3_property_check(self):
        """Method 3: Check using different COM properties and methods."""
        print("\n📊 Method 3: Property-based Count")
        
        folder_counts = {}
        total_count = 0
        
        def count_folder_properties(folder, path=""):
            nonlocal total_count
            current_path = f"{path}/{folder.Name}" if path else folder.Name
            
            try:
                # Try different ways to get count
                items_count = folder.Items.Count
                
                # Alternative: Use different property access
                try:
                    # Some folders might have additional properties
                    unread_count = folder.UnreadItemCount if hasattr(folder, 'UnreadItemCount') else 'N/A'
                    
                    folder_counts[current_path] = {
                        'items_count': items_count,
                        'unread_count': unread_count,
                        'folder_type': getattr(folder, 'DefaultItemType', 'Unknown')
                    }
                    
                    total_count += items_count
                    
                    if items_count > 0:
                        print(f"  📁 {current_path}: {items_count:,} messages")
                        if unread_count != 'N/A':
                            print(f"     Unread: {unread_count}")
                            
                except Exception as e:
                    folder_counts[current_path] = {'items_count': items_count, 'error': str(e)}
                    total_count += items_count
                    
            except Exception as e:
                print(f"  ❌ Error with properties for {current_path}: {str(e)}")
                folder_counts[current_path] = {'error': str(e)}
            
            # Process subfolders
            try:
                for i in range(1, folder.Folders.Count + 1):
                    subfolder = folder.Folders.Item(i)
                    count_folder_properties(subfolder, current_path)
            except:
                pass
        
        root_folder = self.pst_store.GetRootFolder()
        count_folder_properties(root_folder)
        
        print(f"📊 Method 3 Total: {total_count:,} messages")
        return total_count, folder_counts
    
    def verify_pst_completeness(self):
        """Run all verification methods and compare results."""
        if not self.pst_store:
            print("❌ PST file not opened. Call open_pst_file() first.")
            return False
        
        try:
            print("🔍 Running comprehensive PST verification...")
            print("="*60)
            
            # Run all three methods
            total1, folders1 = self.method1_direct_count()
            total2, folders2 = self.method2_iterative_count()
            total3, folders3 = self.method3_property_check()
            
            # Summary comparison
            print("\n" + "="*60)
            print("📊 VERIFICATION SUMMARY")
            print("="*60)
            
            methods_table = [
                ['Method 1 (Direct Count)', f"{total1:,}"],
                ['Method 2 (Iterative)', f"{total2:,}"],
                ['Method 3 (Properties)', f"{total3:,}"]
            ]
            print(tabulate(methods_table, headers=['Method', 'Total Messages'], tablefmt='grid'))
            
            # Check consistency
            all_totals = [total1, total2, total3]
            if len(set(all_totals)) == 1:
                print(f"\n✅ VERIFICATION SUCCESSFUL!")
                print(f"   All methods agree: {total1:,} total messages")
                return total1
            else:
                print(f"\n⚠️  VERIFICATION INCONSISTENCY DETECTED!")
                print(f"   Method differences found - manual review recommended")
                
                # Show most common result
                from collections import Counter
                count_freq = Counter(all_totals)
                most_common = count_freq.most_common(1)[0]
                print(f"   Most common result: {most_common[0]:,} messages ({most_common[1]} methods)")
                return most_common[0]
                
        except Exception as e:
            print(f"❌ Error during verification: {str(e)}")
            return False
    
    def generate_folder_report(self):
        """Generate detailed folder-by-folder report."""
        print("\n" + "="*60)
        print("📁 DETAILED FOLDER REPORT")
        print("="*60)
        
        try:
            _, folder_counts = self.method1_direct_count()
            
            # Sort folders by message count (descending)
            sorted_folders = sorted(folder_counts.items(), key=lambda x: x[1], reverse=True)
            
            folder_table = []
            for folder_path, count in sorted_folders:
                if count > 0:
                    folder_table.append([folder_path, f"{count:,}"])
            
            print(tabulate(folder_table, headers=['Folder Path', 'Message Count'], tablefmt='grid'))
            
        except Exception as e:
            print(f"❌ Error generating folder report: {str(e)}")


def main():
    """Main function to run PST verification."""
    pst_file_path = r"C:\GitHub-Repos\gvranjesevic@dynamique.com\PSTtoDynamics\PST\gvranjesevic@dynamique.com.001.pst"
    
    print("🔍 PST VERIFICATION TOOL")
    print("="*50)
    print("🎯 Purpose: Independent verification of PST message counts")
    print(f"📁 Target PST: {pst_file_path}")
    
    verifier = PSTVerificationTool(pst_file_path)
    
    try:
        # Open PST file
        if not verifier.open_pst_file():
            sys.exit(1)
        
        # Run verification
        total_messages = verifier.verify_pst_completeness()
        
        # Generate detailed report
        verifier.generate_folder_report()
        
        print(f"\n🎯 FINAL VERIFICATION RESULT: {total_messages:,} total messages")
        
    except KeyboardInterrupt:
        print("\n⚠️  Verification interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        verifier.close_pst_file()


if __name__ == "__main__":
    main() 