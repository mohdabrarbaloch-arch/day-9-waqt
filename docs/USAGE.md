# Usage Guide

## Web app

1. Open the app — it loads Karachi, Pakistan by default with the
   **University of Karachi** calculation method.
2. **Change location**: type a city in the search box (e.g. "Lahore",
   "Makkah", "London"). Pick a suggestion and the times refresh instantly.
3. **Method**: choose any of 16 calculation methods (ISNA, MWL, Umm Al-Qura,
   Diyanet, etc.) — the default matches most Pakistani mosques.
4. **Asr juristic**: toggle Shafi (1 shadow) / Hanafi (2 shadows).
5. **Today's card** shows the next prayer and a live countdown.
6. **Monthly timetable**: browse any month with ← / → arrows; Fridays are
   highlighted in gold, today is highlighted.
7. **Qibla**: the compass draws the bearing to the Kaaba from your location.
   Turn your phone so the white needle points to your compass north — the
   gold needle shows Qibla.
8. **Save locations**: register/login (JWT, bcrypt), tap ♡ Save, and your
   places are one tap away.

## API usage

```bash
# Today's times (Karachi default)
curl "http://localhost:8000/api/times?latitude=24.8607&longitude=67.0011&timezone=Asia/Karachi&method=1"

# Whole month
curl "http://localhost:8000/api/times/month?year=2026&month=8&latitude=24.8607&longitude=67.0011"

# Qibla bearing
curl "http://localhost:8000/api/qibla?latitude=24.8607&longitude=67.0011"

# City search
curl "http://localhost:8000/api/cities?query=lahore"

# Register / login (JWT)
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Ali","email":"ali@example.com","password":"secret123"}'
```

## Accuracy notes

- The engine implements the standard solar-position and prayer-time algorithms
  (Meeus low-precision series; refraction + solar radius 0.833°).
- Typical error vs. published timetables: **±1 minute**.
- Always confirm official timings with your local mosque for Ramadan and
  Eid announcements.
