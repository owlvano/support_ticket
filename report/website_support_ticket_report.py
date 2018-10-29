# -*- coding: utf-8 -*-
from odoo import fields, models, tools, _
import logging
_logger = logging.getLogger(__name__)

class WebsiteSupportTicketReport(models.Model):

    _name = "website.support.ticket.report"
    _description = "Website Support Ticket Report"
    _auto = False

    ticket_name = fields.Char('Ticket Name', readonly=True)
    description = fields.Text('Description', readonly=True)
    priority_id = fields.Many2one('website.support.ticket.priority', 'Priority', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    category = fields.Many2one('website.support.ticket.categories', 'Category', readonly=True)
    sub_category_id = fields.Many2one('website.support.ticket.subcategory', 'Sub Category', readonly=True)
    state = fields.Char('State', readonly=True)
    user_id = fields.Many2one('res.users', 'Assigned User', readonly=True)

    created_nbr = fields.Integer('# of Created Tickets', readonly=True)
    closed_nbr = fields.Integer('# of Closed Tickets', readonly=True)
    not_closed_nbr = fields.Integer('# of Not Closed Tickets', readonly=True)
    close_time_days = fields.Integer('Average Close Time (in days)', group_operator='avg', readonly=True)

    def _select(self, select_dict):
        close_comment_string = _("Close Comment")
        select_str = """
             SELECT
                    wst.id as id,
                    concat( '#', wst.ticket_number, '; %s: ' || wst.close_comment) as ticket_name,
        """ % close_comment_string + """
                    wst.description as description,
                    wst.priority_id as priority_id,
                    p.id as partner_id,
                    p.parent_id as company_id,
                    wst.category as category,
                    wst.sub_category_id as sub_category_id,
                    s.name as state,
                    wst.user_id as user_id,
                    %(created_nbr)s as created_nbr,
                    %(closed_nbr)s as closed_nbr,
                    %(not_closed_nbr)s as not_closed_nbr,
                    %(close_time_days)s as close_time_days
        """ % select_dict
        return select_str

    def _select_dict(self, where_dict, select_argument=1):
        basic_select = "( SELECT %s" % select_argument

        select_dict = {
                "created_nbr" : """
                        %s
                        %s
                    )
                    """ % (basic_select, where_dict["where_create_date_in_period"]),
                "closed_nbr" : """
                        %s
                        WHERE %s
                        %s
                    )
                    """ % (basic_select, where_dict["where_closed"], where_dict["where_close_date_in_period"]),
                "not_closed_nbr" : """
                        %s
                        WHERE NOT %s
                        %s
                    )
                    """ % (basic_select, where_dict["where_closed"], where_dict["where_create_date_before_date_to"]),
                "close_time_days" : """
                    ( SELECT %s
                    )
                    """ % where_dict["select_close_days"]
            } 
        
        return select_dict

    def _where_dict(self, date_from, date_to):
        where_dict = {
                "where_closed": "(s.name='Customer Closed' or s.name='Staff Closed')",
                "where_create_date_in_period": "",
                "where_close_date_in_period": "",
                "where_create_date_before_date_to": "",
                "select_close_days": "NULL"
            }
        if date_from and date_to:                     
            where_dict["where_create_date_in_period"] = " WHERE (wst.create_date >= '%s' AND wst.create_date <= '%s') " % (date_from, date_to)
            where_dict["where_close_date_in_period"] = "AND (wst.close_date >= '%s' AND wst.close_date <= '%s')" % (date_from, date_to)
            where_dict["where_create_date_before_date_to"] = "AND (wst.create_date <= '%s')" % (date_to)
            where_dict["select_close_days"] = """
                    wst.close_date::date - wst.create_date::timestamp::date
                    WHERE %(where_closed)s %(where_close_date_in_period)s
                """ % where_dict
        
        return where_dict

    def _where(self, select_dict):
        where_str = """
            WHERE %(created_nbr)s OR %(closed_nbr)s OR %(not_closed_nbr)s
        """ % select_dict
        return where_str

    def _group_by(self):
        group_by_str = """
                GROUP BY
                    wst.id,
                    ticket_name,
                    wst.description,
                    wst.priority_id,
                    p.id,
                    p.parent_id,
                    wst.category,
                    wst.sub_category_id,
                    s.name,
                    wst.user_id
        """
        return group_by_str

    def init(self, date_from=False, date_to=False):
        tools.drop_view_if_exists(self._cr, self._table)

        where_dict = self._where_dict(date_from, date_to)
        select_dict = self._select_dict(where_dict)
        condition_dict = self._select_dict(where_dict, "True")
        query_string = """
            CREATE OR REPLACE VIEW %s as
            %s
            FROM website_support_ticket wst
                left join website_support_ticket_states s on (wst.state = s.id)
                left join res_partner p on (wst.partner_id = p.id)
            %s
            %s
        """ % (self._table, self._select(select_dict), self._where(condition_dict), self._group_by())
        self._cr.execute(query_string)
        _logger.debug("Query executed: ")
        _logger.debug(query_string)

