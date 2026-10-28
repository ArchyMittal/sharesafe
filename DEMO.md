# ShareSafe — Demo Cheat Sheet 🎯

## How to Run

```bash
cd /Users/rishi/Desktop/chatbot
PYTHONPATH=codehack ./venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Open **http://127.0.0.1:8001** in Chrome.

> **Reset data between demos**: `cp codehack/data/requests.json.bak codehack/data/requests.json`  
> (Copy an empty `[]` back to requests.json and reset resources.json r1 status to `"available"`)

---

## Live Demo Script — The Complete Journey

### Step 1 · Browse (30 sec)
- Default user: **Alice Chen** (owner of Oscilloscope, 3D Printer, Rooftop Space)
- Point to the 6 resource cards — status pills, categories, locations
- Show filter pills: "Available" → "All"
- Click **Oscilloscope** card → opens Detail view

### Step 2 · Request (30 sec)
- Switch user to **Bob Patel** (top-right "I am:" dropdown)
- On the Oscilloscope detail page, click **"📬 Request to Borrow"**
- Fill: Start = today, End = tomorrow, Message = "Need it for Lab 3 circuit analysis"
- Click **Send Request** → green toast + status flips to 🟡 Requested

### Step 3 · Owner Approves (30 sec)
- Switch user back to **Alice Chen**
- Click **Dashboard** in nav → "My Listings" tab
- See Bob's request under **Pending Approval** with his message
- Click **✅ Approve** → blue toast, request moves out

### Step 4 · Check Out (20 sec)
- Switch user to **Bob Patel**
- Dashboard → **"My Borrows"** tab
- See Oscilloscope under **"Ready to Check Out"**
- Click **📦 Check Out Now** → green toast, resource is now 🔴 Checked Out

### Step 5 · Return (20 sec)
- Still as **Bob Patel**, same dashboard panel
- Oscilloscope is now under **"Currently Have Out"**
- Click **🔄 Return Item** → type condition note: "Returned in great condition!"
- Click **Confirm Return** → green toast, resource goes back to 🟢 Available

### Step 6 · View History (20 sec)
- Click **History** in the nav
- Select "Oscilloscope (4-Channel, 200 MHz)" from dropdown
- Full timeline shows: Requested → Approved → Checked Out → Returned with condition note

**Total demo time: ~3 minutes** ✅

---

## Judges' Questions — Canned Answers

| Question | Answer |
|---|---|
| "How does auth work?" | Role simulation via dropdown — ideal for a campus pilot where you trust your peers. Real auth (university SSO) is the obvious next step. |
| "Where is data stored?" | JSON files on disk — perfect for a hackathon. SQLite or Supabase is a 1-hour upgrade. |
| "What stops someone from lying about condition?" | Condition note is a record, not enforced. Future: owner counter-signs the return. |
| "Can you scale this?" | swap `JsonStore` for any DB in one file (`store.py`), no API changes needed. |

---

## API Explorer

Visit **http://127.0.0.1:8001/docs** for interactive Swagger UI with all 9 endpoints.
