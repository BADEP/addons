# Copyright 2018 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models

class ActivityStatement(models.AbstractModel):
    """Model of Activity Statement"""

    _inherit = 'report.partner_statement.activity_statement'
    def _display_lines_sql_q1(self, partners, date_start, date_end, account_type):
        return str(
            self._cr.mogrify(
                """
            SELECT m.name AS move_id, l.partner_id, l.date,
                CASE WHEN (aj.type IN ('sale', 'purchase'))
                    THEN l.name
                    ELSE '/'
                END as name,
                CASE
                    WHEN (aj.type IN ('sale', 'purchase')) AND l.name IS NOT NULL
                        THEN l.ref
                    WHEN aj.type IN ('sale', 'purchase') AND l.name IS NULL
                        THEN m.ref
                    WHEN (aj.type in ('bank', 'cash'))
                        THEN l.ref
                    ELSE ''
                END as ref,
                l.blocked, l.currency_id, l.company_id,
                sum(CASE WHEN (l.currency_id is not null AND l.amount_currency > 0.0)
                    THEN l.amount_currency
                    ELSE l.debit
                END) as debit,
                sum(CASE WHEN (l.currency_id is not null AND l.amount_currency < 0.0)
                    THEN l.amount_currency * (-1)
                    ELSE l.credit
                END) as credit,
                CASE WHEN l.date_maturity is null
                    THEN l.date
                    ELSE l.date_maturity
                END as date_maturity
            FROM account_move_line l
            JOIN account_account aa ON (aa.id = l.account_id)
            JOIN account_account_type at ON (at.id = aa.user_type_id)
            JOIN account_move m ON (l.move_id = m.id)
            JOIN account_journal aj ON (l.journal_id = aj.id)
            WHERE l.partner_id IN %(partners)s
                AND at.type = %(account_type)s
                AND %(date_start)s <= l.date
                AND l.date <= %(date_end)s
                AND m.state IN ('posted')
            GROUP BY l.partner_id, m.name, l.date, l.date_maturity,
                CASE WHEN (aj.type IN ('sale', 'purchase'))
                    THEN l.name
                    ELSE '/'
                END,
                CASE
                    WHEN (aj.type IN ('sale', 'purchase')) AND l.name IS NOT NULL
                        THEN l.ref
                    WHEN aj.type IN ('sale', 'purchase') AND l.name IS NULL
                        THEN m.ref
                    WHEN (aj.type in ('bank', 'cash'))
                        THEN l.ref
                    ELSE ''
                END,
                l.blocked, l.currency_id, l.company_id
        """,
                locals(),
            ),
            "utf-8",
        )