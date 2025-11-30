#!/usr/bin/env python
"""
Update all area code 85 candidates to use 8-digit phone format (without leading 9).
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.candidate.models import Candidate

def update_area85_phones():
    """Update all area code 85 candidates to use 8-digit format."""
    
    print("=" * 70)
    print("Update Area Code 85 Phone Numbers to 8-Digit Format")
    print("=" * 70)
    print()
    
    # Find all candidates with area code 85 and saved whatsapp_phone
    candidates = Candidate.objects.filter(
        phone_number__startswith='85'
    ).exclude(whatsapp_phone__isnull=True).exclude(whatsapp_phone='')
    
    print(f"Found {candidates.count()} candidates with area code 85 and saved WhatsApp format")
    print()
    
    updated_count = 0
    skipped_count = 0
    
    for candidate in candidates:
        phone = candidate.whatsapp_phone
        cleaned = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        
        # Check if it's 11 digits (has the leading 9)
        if len(cleaned) == 11 and cleaned[2] == '9':
            # Convert to 8-digit format (remove the 9)
            new_format = f"{cleaned[:2]} {cleaned[3:7]}-{cleaned[7:]}"
            
            print(f"Updating {candidate.full_name}:")
            print(f"  Old: {phone} (9-digit)")
            print(f"  New: {new_format} (8-digit)")
            
            candidate.whatsapp_phone = new_format
            candidate.save(update_fields=['whatsapp_phone'])
            
            updated_count += 1
        else:
            print(f"Skipping {candidate.full_name}: {phone} (already 8-digit or invalid)")
            skipped_count += 1
    
    print()
    print("=" * 70)
    print(f"✅ Updated {updated_count} candidates")
    print(f"⏭️  Skipped {skipped_count} candidates")
    print("=" * 70)
    print()
    print("All area code 85 candidates will now use 8-digit format!")


if __name__ == '__main__':
    try:
        confirm = input("This will update all area code 85 candidates to 8-digit format. Continue? (y/n): ").strip().lower()
        if confirm == 'y':
            update_area85_phones()
        else:
            print("Cancelled.")
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(0)
