# -*- coding: utf-8 -*-
from odoo import fields, models, tools

class WebsiteSupportTicket(models.Model):

    _name = "website.support.ticket.report"
    _description = "Website Support Ticket Report"
    _auto = False

    create_date = fields.Datetime('Create Date', readonly=True)
    close_time = fields.Datetime(string="Close Time")
    priority_id = fields.Many2one('website.support.ticket.priority', "Priority", readonly=True)
    partner_id = fields.Many2one('res.partner', "Partner", readonly=True)
    company_id = fields.Many2one('res.company', "Company", readonly=True)
    category = fields.Many2one('website.support.ticket.categories', "Category", readonly=True)
    sub_category_id = fields.Many2one('website.support.ticket.subcategory', "Sub Category", readonly=True)
    state = fields.Char("State", readonly=True)
    user_id = fields.Many2one('res.users',"Assigned User", readonly=True)

    created_nbr = fields.Integer('# of Created Tickets', readonly=True)
    closed_nbr = fields.Integer('# of Closed Tickets', readonly=True)
    not_closed_nbr = fields.Integer('# of Not Closed Tickets', readonly=True)
    close_time = fields.Float('Close Time (in days)', digits=(16,1), readonly=True)

    def timestamp_format(self, date):
        return "\"%s\"::timestamp" % date

    def _select(self, date_from, date_to):
        select_str = """
             SELECT
                    wst.id as id,
                    wst.create_date as create_date,
                    wst.close_time as close_time,
                    wst.priority_id as priority_id,
                    wst.partner_id as partner_id,
                    wst.company_id as company_id,
                    wst.category as category,
                    wst.sub_category_id as sub_category_id,
                    s.name as state,
                    wst.user_id as user_id,
                    ( SELECT 1 
                        %(where_created_nbr)s
                    ) as created_nbr,
                    ( SELECT 1 
                        WHERE ( s.name='Customer Closed' or s.name='Staff Closed' ) 
                        %(where_closed_nbr)s
                    ) as closed_nbr,
                    ( SELECT 1 
                        WHERE NOT ( s.name='Customer Closed' or s.name='Staff Closed' )
                        %(where_not_closed_nbr)s
                    ) as not_closed_nbr
        """ % self._select_where_dict(date_from, date_to)
        return select_str

    def _select_where_dict(self, date_from, date_to):
        where_dict = {
                "where_created_nbr": "",
                "where_closed_nbr": "",
                "where_not_closed_nbr": ""
            }
        if date_from and date_to:
            date_from = self.timestamp_format(date_from)
            date_to = self.timestamp_format(date_to)                        
            where_dict = {
                "where_created_nbr": " WHERE ( wst.create_date BETWEEN %s AND %s ) " % ( date_from, date_to ),
                "where_closed_nbr": "AND ( wst.close_time BETWEEN %s AND %s )" % ( date_from, date_to ),
                "where_not_closed_nbr": "AND ( wst.create_date <= %s )" % ( date_to )
            }
        return where_dict

    def _group_by(self):
        group_by_str = """
                GROUP BY
                    wst.id,
                    wst.create_date,
                    wst.priority_id,
                    wst.partner_id,
                    wst.company_id,
                    wst.category,
                    wst.sub_category_id,
                    s.name,
                    wst.user_id
        """
        return group_by_str

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)

        date_from = self.env.context.get('date_from') or False
        date_to = self.env.context.get('date_to') or False

        self._cr.execute("""
            CREATE OR REPLACE VIEW %s as
            %s
            FROM website_support_ticket wst
                left join website_support_ticket_states s on (wst.state = s.id)
            %s
        """ % (self._table, self._select(date_from, date_to), self._group_by()))
