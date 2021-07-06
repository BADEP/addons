# Copyright 2019 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Stock Tier Validation",
    "summary": "Extends the functionality of Stock Pickings to "
               "support a tier validation process.",
    "version": "14.0.1.0.0",
    "category": "Inventory",
    "website": "https://badep.ma",
    "author": "BADEP, Open Source Integrators, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": False,
    "depends": [
        "stock",
        "base_tier_validation",
    ],
    "data": [
        "views/stock_picking_view.xml",
    ],
}