# ShareSafe 🔐

> **Campus Equipment & Space Sharing Platform**  
> Safely share campus instruments, production gear, fabrication tools, and collaboration spaces with verified student credentials, fair-access allowances, contactless smart locker dispatch, and full chain-of-custody audit logs.

---

## 🌟 Key Features

- **Campus Equipment Catalog**: Rich visual catalog with live status pills (`Available Now`, `Due Today`, `In Use`), bay/locker tags, prerequisites, and max duration rules.
- **Fair-Access Allocation**: NetID-verified allowance tracking (e.g. 1 of 2 loan slots active) to prevent hoarding during peak finals.
- **Interactive Reservation Drawer**: Smooth slide-out reservation panel with date/time pickers, academic project justification, and lab safety checklist verification.
- **Custodian & Owner Review**: Queue for lab managers to authorize or decline student reservation requests.
- **Contactless Dispatch Kiosk**: Smart locker bay unlock simulation for pick-up and check-in return with condition verification.
- **Chain-of-Custody Audit Trail**: Immutable transaction log tracking checkout timestamps, borrowers, custodians, and return condition inspections.
- **Multi-Role Profile Switcher**: Instantly toggle between Student Borrowers (e.g., Maya Lin) and Lab Custodians (e.g., Marcus Vance).

---

## 🛠 Tech Stack

- **Backend**: Python 3, FastAPI, Pydantic v2, Uvicorn
- **Storage**: Atomic thread-safe JSON-on-disk store with file locking (`JsonStore`)
- **Frontend**: Vanilla JavaScript (SPA architecture), Tailwind CSS with custom design tokens, Google Material Symbols, Plus Jakarta Sans & Inter typography

---

## 🚀 Quickstart

### 1. Clone the repository
```bash
git clone https://github.com/ay10101/sharesafe.git
cd sharesafe
```

### 2. Set up virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the application
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

---

## 📂 Project Structure

```
├── app/
│   ├── main.py              # FastAPI application and route endpoints
│   ├── sharesafe_models.py  # Pydantic v2 schemas
│   └── store.py             # Thread-safe JSON persistence layer
├── data/
│   ├── requests.json        # Borrow request records
│   ├── resources.json       # Equipment catalog seed data
│   └── users.json           # Campus users and profile metadata
├── static/
│   ├── index.html           # Main SPA layout with Tailwind styling
│   ├── sharesafe.css        # Additional transitions and toast styles
│   └── sharesafe.js         # Frontend controller and API integration
├── DEMO.md                  # Hackathon live demo walkthrough
├── requirements.txt         # Python dependencies
└── README.md
```

---

## 📜 License
MIT License. Built for university research & collaborative campus maker hubs.
