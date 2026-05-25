# SFA Core — Sales Force Automation Platform

**Company:** Hema Beverages
**Industry:** FMCG
**Markets:** Uganda (active), South Sudan & DRC (planned)

Built on Frappe v15 + ERPNext v15.

## Installation

```bash
bench get-app https://github.com/hemabeverages/sfa_core.git
bench --site hema.local install-app sfa_core
```

## Development

```bash
cd apps/sfa_core && npm install && npm run build
bench build --apps sfa_core
bench --site hema.local migrate
```

## Local Development Install (no GitHub required)

```bash
# From your bench directory:
cp -r /path/to/sfa_core_fixed ./apps/sfa_core
bench --site hema.local install-app sfa_core

# Build frontend assets:
cd apps/sfa_core
npm install
npm run build
cd ../..
bench build --apps sfa_core

# Apply DB migrations:
bench --site hema.local migrate
```

## Full deployment sequence (first time)

```bash
# 1. Get and install app
bench get-app /path/to/sfa_core   # or GitHub URL once repo is set up
bench --site hema.local install-app sfa_core

# 2. Build frontend
cd apps/sfa_core && npm install && npm run build && cd ../..
bench build --apps sfa_core

# 3. Migrate DB (creates all DocTypes)
bench --site hema.local migrate

# 4. Restart
bench restart

# 5. Verify
bench --site hema.local console
# >>> frappe.db.exists("DocType", "SFA Visit")  # Should return "SFA Visit"
```

## Required Frappe/ERPNext versions

- Frappe v15.x
- ERPNext v15.x  
- Python >= 3.10
- Node >= 18

## After install — check these in Frappe Desk

1. Go to Workspace → SFA (should appear after install)
2. Check Role list — SFA Manager, SFA Supervisor, SFA Rep, SFA Viewer should exist
3. Check DocType list — all SFA* doctypes should be present
4. Open sfa-dashboard page — should load (even if empty until data exists)
