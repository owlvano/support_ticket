# -*- coding: utf-8 -*-
from odoo import api, fields, models

class WebsiteSupportTicket(models.Model):

    _inherit = "website.support.ticket"

    @api.onchange('sub_category_id')
    def _onchange_sub_category_id(self):
        self.user_id= self.sub_category_id.user_id

class WebsiteSupportTicketSubCategories(models.Model):

    _inherit = "website.support.ticket.subcategory"

    user_id = fields.Many2one('res.users', string="Assigned User")