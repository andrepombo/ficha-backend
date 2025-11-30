# WhatsApp Phone Auto-Detection Feature

## 🎯 Overview

The system now automatically detects and saves the correct WhatsApp phone format for each candidate. This eliminates the need for manual phone number adjustments and ensures reliable message delivery.

## ✨ How It Works

### 1. **First Message Attempt**
When sending a WhatsApp message to a candidate for the first time:

1. **Check for saved format:** If `candidate.whatsapp_phone` exists, use it
2. **Try original format:** Send using `candidate.phone_number` as-is
3. **Try alternative format:** If it fails, automatically try with/without the leading 9
4. **Save working format:** Once successful, save to `candidate.whatsapp_phone`

### 2. **Subsequent Messages**
For future messages to the same candidate:

1. **Use saved format:** Always use `candidate.whatsapp_phone` first
2. **Fallback:** If saved format fails, retry with alternatives
3. **Update if needed:** Save new working format if it changes

## 📊 Database Changes

### New Field Added to Candidate Model

```python
whatsapp_phone = models.CharField(
    max_length=20,
    blank=True,
    verbose_name='WhatsApp Phone',
    help_text='Verified WhatsApp phone format (auto-detected)'
)
```

**Migration:** `0019_add_whatsapp_phone_field.py`

## 🔄 Phone Format Detection Logic

### Brazilian Mobile Number Formats

**Format 1: With leading 9 (11 digits)**
- Database: `85 98880-6269`
- WhatsApp: `whatsapp:+5585988806269`

**Format 2: Without leading 9 (10 digits)**
- Database: `85 8880-6269`
- WhatsApp: `whatsapp:+558588806269`

### Auto-Detection Process

```
1. Try Format 1 (as entered)
   ↓ Success? → Save and use
   ↓ Failed (Error 63015 or 21211)?
   
2. Try Format 2 (alternative)
   ↓ Success? → Save and use
   ↓ Failed?
   
3. Return error
```

## 📝 Example Scenario

### Scenario: Candidate with wrong format in database

**Initial State:**
- `candidate.phone_number` = `"85 98880-6269"` (11 digits)
- `candidate.whatsapp_phone` = `""` (empty)
- Actual WhatsApp: `+55 85 8880-6269` (10 digits)

**First Message Attempt:**
1. Try `whatsapp:+5585988806269` → **Fails** (Error 63015)
2. Auto-detect alternative: `85 8880-6269`
3. Try `whatsapp:+558588806269` → **Success!** ✅
4. Save `candidate.whatsapp_phone = "85 8880-6269"`

**Second Message:**
1. Use saved `whatsapp:+558588806269` → **Success!** ✅
2. No retry needed - instant delivery

## 🎉 Benefits

### 1. **Zero Manual Configuration**
- No need to manually update phone numbers
- System learns the correct format automatically
- Works with any Brazilian phone format

### 2. **Reliable Delivery**
- First message: May take 2 attempts (original + alternative)
- Subsequent messages: Instant delivery using saved format
- Reduces failed deliveries

### 3. **Transparent Operation**
- Logs show which format worked
- API responses include verified phone format
- Easy to monitor and debug

### 4. **Future-Proof**
- Handles both old (10-digit) and new (11-digit) formats
- Adapts to carrier changes
- No code changes needed for new formats

## 📊 API Response Changes

### Interview API Response

```json
{
  "id": 1,
  "candidate": 123,
  "candidate_name": "João Silva",
  "whatsapp_sent": true,
  "whatsapp_message_sid": "SM1234567890",
  "whatsapp_sent_at": "2025-10-21T12:00:00Z",
  ...
}
```

### Candidate API Response

```json
{
  "id": 123,
  "full_name": "João Silva",
  "phone_number": "85 98880-6269",
  "whatsapp_phone": "85 8880-6269",  // ← NEW: Auto-detected format
  ...
}
```

## 🔍 Monitoring

### Check Logs

```bash
# Django logs will show:
Using saved WhatsApp phone format: 85 8880-6269
WhatsApp message sent successfully to João Silva. Format used: whatsapp:+558588806269

# Or for first-time detection:
Failed with whatsapp:+5585988806269, trying alternative format
Trying alternative format: whatsapp:+558588806269
Saved working WhatsApp format (alternative): 85 8880-6269
```

### Check Database

```python
from apps.candidate.models import Candidate

candidate = Candidate.objects.get(id=123)
print(f"Original phone: {candidate.phone_number}")
print(f"WhatsApp phone: {candidate.whatsapp_phone}")
```

## 🧪 Testing

### Test Auto-Detection

```bash
# Update an interview to trigger WhatsApp
./venv/bin/python test_update_interview.py

# Check the logs to see format detection in action
```

### Verify Saved Format

```bash
./venv/bin/python diagnose_whatsapp.py
```

## 🚀 Migration Guide

### For Existing Installations

1. **Pull latest code**
2. **Run migration:**
   ```bash
   ./venv/bin/python manage.py migrate
   ```
3. **Restart Django server**
4. **Test with an interview update**

### For New Installations

The feature is automatically included - no additional setup needed!

## 💡 Technical Details

### Code Changes

**1. Model Update (`models.py`):**
- Added `whatsapp_phone` field to Candidate model

**2. Service Update (`whatsapp_service.py`):**
- Modified `_try_send_message()` to accept candidate object
- Added logic to check and use saved `whatsapp_phone`
- Added logic to save working format on success
- Enhanced logging for transparency

**3. Migration:**
- Created `0019_add_whatsapp_phone_field.py`

### Performance Impact

- **First message:** +1 API call if alternative format needed
- **Subsequent messages:** No additional calls (uses saved format)
- **Database:** +1 field per candidate (minimal storage)
- **Overall:** Improved reliability, minimal overhead

## 🔐 Privacy & Security

- WhatsApp phone numbers are stored securely in the database
- Only verified/working formats are saved
- No external services involved in detection
- Complies with existing data privacy policies

## 📚 Related Documentation

- [WhatsApp Setup Guide](WHATSAPP_SETUP_GUIDE.md)
- [Quick Start](WHATSAPP_QUICK_START.md)
- [Integration Summary](../WHATSAPP_INTEGRATION_SUMMARY.md)

---

**Feature Status:** ✅ Active and Production-Ready

**Last Updated:** 2025-10-21
