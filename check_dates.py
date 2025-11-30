import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.candidate.models import Candidate
from collections import Counter

candidates = Candidate.objects.all().order_by('applied_date')
dates = [c.applied_date for c in candidates]

print(f"Total candidates: {len(candidates)}")
print(f"Unique dates: {len(set(dates))}")
print("\nFirst 10 candidates by date:")
for c in candidates[:10]:
    print(f"  {c.applied_date} - {c.full_name}")

print("\nLast 10 candidates by date:")
for c in candidates[30:40]:
    print(f"  {c.applied_date} - {c.full_name}")

print("\nDate distribution:")
for date, count in Counter(dates).most_common():
    print(f"  {date}: {count} candidates")
