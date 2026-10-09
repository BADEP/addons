# base_upgrade_path: TODO for the dev agents

## Purpose

This module is the basis of the **Migration Analysis** for an Odoo upgrade.
The method is in BADEP's Odoo Knowledge: Logistics › ERP › ERP · Migration
Analysis. The Excel template it replaces is
`Work/Logistics/ERP/ERP_Migration_Inventory_Template.xlsx`.

The analysis is purely technical: code analysis plus database analysis. The goal
of a migration is the same processes in the new version, with minimum change
management and minimum downtime. Enhancements are always a separate project.

The module runs **in the customer database** being analysed. Its results are
then brought into the BADEP database. Today it checks, for each installed
module, whether it is available in a target version (Odoo standard, apps.odoo.com,
PyPI/OCA, and the GitHub repos in `ir.module.repo`). It also counts Python and XML
lines.

## TODO

### 1. Settings
- [ ] Move `target` from a per-module field to an `ir.config_parameter`, as the
      existing code comment says. Allow every target version, not only 17.0.
- [ ] Record the source version, the edition (Community / Enterprise), the
      database size and the filestore size.
- [ ] Upgrade path: the Odoo upgrade service for Enterprise, OpenUpgrade for
      Community. For Community, check OpenUpgrade coverage per module for the
      target version.

### 2. Data per module
- [ ] "Holds data": for each installed module, count the records of the models
      it defines, and the non-empty values of the fields it adds. A module or
      field that holds data cannot be removed without losing that data.
- [ ] "Really used": records created or written in the last 12 months, per model.

### 3. Customizations outside modules
Inventory each of the following. Record how many there are and whether it holds
data, and link it to the owning module where there is one.
- [ ] **Studio data**: everything under `studio_customization` (`ir.model.data`
      with module `studio_customization`), plus `x_studio_*` fields.
- [ ] **Custom models**: `ir.model` with `state = 'manual'`, and their record counts.
- [ ] **Custom fields**: `ir.model.fields` with `state = 'manual'`, and their
      non-empty counts.
- [ ] **Custom views**: `ir.ui.view` records created from the UI (no
      `ir.model.data`, or module `studio_customization`). Also views from modules
      whose arch was changed in the database (`arch_updated`).
- [ ] **Server actions**: `ir.actions.server` not owned by a module, with their
      code.
- [ ] **Scheduled actions**: `ir.cron` not owned by a module, plus the active
      crons that call other systems.
- [ ] **Automated actions**: `base.automation` (when installed).
- [ ] **Reports and mail templates** changed in the database
      (`ir.actions.report`, `ir.ui.view` QWeb, `mail.template`).

### 4. Decision and estimate
- [ ] Per module and per customization, record a decision: Migrate / Remove
      (only if it holds no data and is unused) / Flag (enhancement) /
      Standard (no work). Also record a size (Small / Medium / Large) and an
      estimate in hours.
- [ ] Keep an Enhancement list, separate from the migration scope.
- [ ] Summary: migration hours, automated script set-up, test rounds (% of
      modules + script), quotation hours, and down-payment (monthly hours ×
      (1 + payment months)). Use the same rules as the Excel template.

### 5. Continuous migration
- [ ] Generate the input files of the automated migration script from the
      decisions: `pre-remove-modules.txt`, `post-install-modules.txt`,
      `post-remove-modules.txt`, and stubs for `pre-migrate.py` /
      `post-migrate.py`.

### 6. Export and versions
- [ ] Export the full inventory to Excel (same layout as the template) and as
      JSON, for import into the BADEP database.
- [ ] Port forward to 15.0 → 19.0 (and 20.0), so the module can be installed on
      any customer database we analyse.
- [ ] Tests for the data counts and the customization inventory.
