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
