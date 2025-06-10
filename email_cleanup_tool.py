#!/usr/bin/env python3
"""
Email Cleanup Tool
Removes email addresses from email_addresses.csv that already exist in Dynamics 365 contacts.
This helps identify PST email addresses that are NOT in the CRM system.

Requirements:
- pip install pandas tabulate
"""

import pandas as pd
from datetime import datetime
from tabulate import tabulate
import sys


class EmailCleanupTool:
    def __init__(self, pst_emails_file, dynamics_contacts_file):
        """Initialize the email cleanup tool."""
        self.pst_emails_file = pst_emails_file
        self.dynamics_contacts_file = dynamics_contacts_file
        self.pst_emails_df = None
        self.dynamics_contacts_df = None
        self.cleaned_emails_df = None
        self.dynamics_email_set = set()
        
        print("🧹 EMAIL CLEANUP TOOL")
        print("="*40)
        print("🎯 Purpose: Remove PST emails that already exist in Dynamics 365 CRM")
        print(f"📧 PST Emails File: {self.pst_emails_file}")
        print(f"🏢 Dynamics Contacts File: {self.dynamics_contacts_file}")
        print()
    
    def load_data(self):
        """Load both CSV files."""
        try:
            print("📂 Loading data files...")
            
            # Load PST emails
            print(f"   📧 Loading PST emails from {self.pst_emails_file}")
            self.pst_emails_df = pd.read_csv(self.pst_emails_file)
            print(f"   ✅ Loaded {len(self.pst_emails_df)} PST email addresses")
            
            # Load Dynamics contacts
            print(f"   🏢 Loading Dynamics contacts from {self.dynamics_contacts_file}")
            self.dynamics_contacts_df = pd.read_csv(self.dynamics_contacts_file)
            print(f"   ✅ Loaded {len(self.dynamics_contacts_df)} Dynamics 365 contacts")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {str(e)}")
            return False
    
    def extract_dynamics_emails(self):
        """Extract all email addresses from Dynamics 365 contacts."""
        try:
            print("\n📧 Extracting email addresses from Dynamics 365 contacts...")
            
            # Get all email columns from Dynamics contacts
            email_columns = ['primary_email', 'secondary_email', 'tertiary_email']
            all_dynamics_emails = set()
            
            for column in email_columns:
                if column in self.dynamics_contacts_df.columns:
                    # Get non-null, non-empty emails from this column
                    emails = self.dynamics_contacts_df[column].dropna()
                    
                    # Convert to string and filter out empty values
                    emails = emails.astype(str)
                    emails = emails[emails.str.strip() != '']  # Remove empty strings
                    emails = emails[emails != 'nan']  # Remove NaN strings
                    
                    if len(emails) > 0:
                        # Convert to lowercase for case-insensitive comparison
                        emails_lower = emails.str.lower()
                        all_dynamics_emails.update(emails_lower.tolist())
                        
                        print(f"   📨 Found {len(emails)} emails in {column}")
                    else:
                        print(f"   📨 No emails found in {column}")
            
            self.dynamics_email_set = all_dynamics_emails
            print(f"   ✅ Total unique Dynamics 365 emails: {len(self.dynamics_email_set)}")
            
            # Show some examples
            print(f"   🔍 Sample Dynamics emails:")
            sample_emails = list(self.dynamics_email_set)[:5]
            for email in sample_emails:
                print(f"      - {email}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error extracting Dynamics emails: {str(e)}")
            return False
    
    def clean_pst_emails(self):
        """Remove PST emails that exist in Dynamics 365."""
        try:
            print("\n🧹 Cleaning PST email addresses...")
            
            # Convert PST emails to lowercase for comparison
            pst_emails_lower = self.pst_emails_df['email_address'].str.lower()
            
            # Find emails that are NOT in Dynamics 365
            mask_not_in_dynamics = ~pst_emails_lower.isin(self.dynamics_email_set)
            
            # Keep only emails that are NOT in Dynamics 365
            self.cleaned_emails_df = self.pst_emails_df[mask_not_in_dynamics].copy()
            
            # Calculate removal statistics
            original_count = len(self.pst_emails_df)
            cleaned_count = len(self.cleaned_emails_df)
            removed_count = original_count - cleaned_count
            
            print(f"   📊 Original PST emails: {original_count:,}")
            print(f"   ❌ Emails removed (already in CRM): {removed_count:,}")
            print(f"   ✅ Emails remaining (NOT in CRM): {cleaned_count:,}")
            print(f"   📈 Removal percentage: {(removed_count/original_count)*100:.1f}%")
            
            # Show which emails were removed
            if removed_count > 0:
                removed_emails = self.pst_emails_df[~mask_not_in_dynamics]
                print(f"\n   🗑️  Removed emails (first 10):")
                for idx, row in removed_emails.head(10).iterrows():
                    print(f"      - {row['email_address']} ({row['display_name']}) - Count: {row['count']}")
                
                if removed_count > 10:
                    print(f"      ... and {removed_count - 10} more")
            
            return True
            
        except Exception as e:
            print(f"❌ Error cleaning PST emails: {str(e)}")
            return False
    
    def save_cleaned_emails(self, output_file=None):
        """Save the cleaned email addresses to a new CSV file."""
        try:
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"email_addresses_cleaned_{timestamp}.csv"
            
            print(f"\n💾 Saving cleaned emails to {output_file}...")
            
            # Save to CSV
            self.cleaned_emails_df.to_csv(output_file, index=False)
            
            print(f"   ✅ Saved {len(self.cleaned_emails_df)} cleaned email addresses")
            
            return output_file
            
        except Exception as e:
            print(f"❌ Error saving cleaned emails: {str(e)}")
            return None
    
    def show_summary_statistics(self):
        """Display summary statistics of the cleanup process."""
        try:
            print(f"\n📊 EMAIL CLEANUP SUMMARY")
            print("="*50)
            
            original_count = len(self.pst_emails_df)
            cleaned_count = len(self.cleaned_emails_df)
            removed_count = original_count - cleaned_count
            
            # Overview statistics
            overview_stats = [
                ['Original PST Emails', f"{original_count:,}"],
                ['Emails in Dynamics 365', f"{len(self.dynamics_email_set):,}"],
                ['Emails Removed (Duplicates)', f"{removed_count:,}"],
                ['Emails Remaining (New)', f"{cleaned_count:,}"],
                ['Removal Rate', f"{(removed_count/original_count)*100:.1f}%"]
            ]
            print(tabulate(overview_stats, headers=['Metric', 'Value'], tablefmt='grid'))
            
            if cleaned_count > 0:
                # Top remaining emails by count
                print(f"\n📧 Top 15 Remaining Emails (NOT in CRM):")
                top_emails = self.cleaned_emails_df.nlargest(15, 'count')
                email_table = []
                for idx, row in top_emails.iterrows():
                    email_table.append([
                        row['email_address'][:40] + ('...' if len(row['email_address']) > 40 else ''),
                        row['display_name'][:30] + ('...' if len(str(row['display_name'])) > 30 else ''),
                        row['count']
                    ])
                
                print(tabulate(email_table, headers=['Email Address', 'Display Name', 'Count'], tablefmt='grid'))
                
                # Domain analysis of remaining emails
                print(f"\n🌐 Top 10 Domains in Remaining Emails:")
                domains = self.cleaned_emails_df['email_address'].str.split('@').str[1]
                domain_counts = domains.value_counts().head(10)
                domain_table = [[domain, count] for domain, count in domain_counts.items()]
                print(tabulate(domain_table, headers=['Domain', 'Email Count'], tablefmt='grid'))
                
                # Count distribution
                print(f"\n📈 Email Count Distribution (Remaining Emails):")
                count_stats = self.cleaned_emails_df['count'].describe()
                count_table = [
                    ['Total Emails', f"{count_stats['count']:.0f}"],
                    ['Average Count per Email', f"{count_stats['mean']:.1f}"],
                    ['Median Count', f"{count_stats['50%']:.0f}"],
                    ['Min Count', f"{count_stats['min']:.0f}"],
                    ['Max Count', f"{count_stats['max']:.0f}"],
                    ['Total Message Volume', f"{self.cleaned_emails_df['count'].sum():,}"]
                ]
                print(tabulate(count_table, headers=['Metric', 'Value'], tablefmt='grid'))
            
            print("\n" + "="*50)
            
        except Exception as e:
            print(f"⚠️  Error generating summary: {str(e)}")
    
    def run(self):
        """Run the complete email cleanup process."""
        try:
            print("🚀 Starting Email Cleanup Process")
            print("="*35)
            
            # Step 1: Load data
            if not self.load_data():
                return False
            
            # Step 2: Extract Dynamics emails
            if not self.extract_dynamics_emails():
                return False
            
            # Step 3: Clean PST emails
            if not self.clean_pst_emails():
                return False
            
            # Step 4: Save cleaned emails
            output_file = self.save_cleaned_emails()
            if not output_file:
                return False
            
            # Step 5: Show summary
            self.show_summary_statistics()
            
            print(f"\n🎉 Email cleanup completed successfully!")
            print(f"📁 Cleaned emails saved to: {output_file}")
            print(f"💡 These are PST emails that are NOT in your Dynamics 365 CRM")
            print(f"💡 Consider adding these as new contacts in your CRM system")
            
            return True
            
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            return False


def main():
    """Main function to run the email cleanup tool."""
    # File paths
    pst_emails_file = "email_addresses.csv"
    dynamics_contacts_file = "dynamics_contacts_20250610_155933.csv"
    
    print("🧹 EMAIL CLEANUP TOOL")
    print("="*25)
    print("🎯 Purpose: Clean PST emails by removing duplicates already in Dynamics 365")
    print(f"📧 Input: {pst_emails_file}")
    print(f"🏢 Reference: {dynamics_contacts_file}")
    print()
    
    # Create cleanup tool instance
    cleanup_tool = EmailCleanupTool(pst_emails_file, dynamics_contacts_file)
    
    try:
        # Run the cleanup process
        success = cleanup_tool.run()
        
        if success:
            print("\n✅ Process completed successfully!")
        else:
            print("\n❌ Process failed. Check the error messages above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️  Process interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 