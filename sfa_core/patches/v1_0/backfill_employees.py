"""
Stage 2c — backfill Employees for EXISTING Sales Persons.

DRY-RUN FIRST. With DRY_RUN = True (default) it creates NOTHING — it only logs what
it *would* provision. Review the log (bench --site hema.local console, or the patch
output), then set DRY_RUN = False and re-run via migrate to actually create+link.

Per §3 discipline: verify before committing the destructive/creative step.

Target set (confirmed): real people with a custom_user_id, excluding the Sales Team
root node and the two test records. Resolves to: Ramesh, Sumanth, Tharun.

Registered as: sfa_core.patches.v1_0.backfill_employees
Idempotent: skips any Sales Person already linked to an existing Employee.
"""

import frappe
from sfa_core.field_sfa.doc_events.sales_person import (
    _is_provisionable,
    _create_and_link,
)

# ──────────────────────────────────────────────────────────────────────────────
DRY_RUN = False   # <-- set to False ONLY after reviewing the dry-run log
# ──────────────────────────────────────────────────────────────────────────────


def execute():
    sales_persons = frappe.get_all(
        "Sales Person",
        fields=["name", "sales_person_name", "custom_user_id", "custom_territory",
                "custom_employee", "is_group", "enabled"],
    )

    to_provision, skipped = [], []
    for sp in sales_persons:
        doc = frappe.get_doc("Sales Person", sp.name)
        if not _is_provisionable(doc):
            skipped.append((sp.name, "not provisionable (group/test/no user_id)"))
            continue
        if sp.custom_employee and frappe.db.exists("Employee", sp.custom_employee):
            skipped.append((sp.name, f"already linked -> {sp.custom_employee}"))
            continue
        to_provision.append(doc)

    lines = ["[backfill_employees] DRY_RUN=%s" % DRY_RUN, "WOULD PROVISION:"]
    for doc in to_provision:
        lines.append(f"  + {doc.name}  (user_id={doc.get('custom_user_id')}, "
                     f"territory={doc.get('custom_territory')})")
    lines.append("SKIPPED:")
    for name, reason in skipped:
        lines.append(f"  - {name}: {reason}")
    report = "\n".join(lines)

    # Print to migrate output AND persist to error log for later inspection.
    print(report)
    frappe.log_error(report, "backfill_employees report")

    if DRY_RUN:
        print("[backfill_employees] DRY_RUN — no Employees created. "
              "Set DRY_RUN=False and re-migrate to apply.")
        return

    created = []
    for doc in to_provision:
        _create_and_link(doc)
        created.append((doc.name, doc.custom_employee))
    frappe.db.commit()

    done = "\n".join(f"  ✓ {sp} -> {emp}" for sp, emp in created)
    print(f"[backfill_employees] CREATED {len(created)} Employee links:\n{done}")
