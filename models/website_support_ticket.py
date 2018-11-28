# -*- coding: utf-8 -*-
from odoo import api, fields, models

class WebsiteSupportTicket(models.Model):

    _inherit = "website.support.ticket"

    active = fields.Boolean(default=True, help="The active field allows you to hide the category without removing it.")

    @api.onchange('sub_category_id')
    def _onchange_sub_category_id(self):
        # Update responsiblue user if he's empty
        if not self.user_id:
            self.user_id = self.sub_category_id.user_id
        # Update priority based on subcategory
        self.priority_id = self.sub_category_id.priority_id

    @api.onchange('category')
    def _onchange_category(self):
        self.sub_category_id = ""

    @api.model
    def create(self, vals):
        new_id = super(WebsiteSupportTicket, self).create(vals)

        #Automatically assign a responsible user
        if new_id.sub_category_id.user_id:
            new_id.user_id = new_id.sub_category_id.user_id

        #Automatically assign a priority
        if new_id.sub_category_id.priority_id:
            new_id.priority_id = new_id.sub_category_id.priority_id

        return new_id
   

class WebsiteSupportTicketSubCategories(models.Model):

    _inherit = "website.support.ticket.subcategory"

    def _default_priority_id(self):
        default_priority = self.env['website.support.ticket.priority'].search([('sequence','=','1')])
        return default_priority[0]

    active = fields.Boolean(default=True, help="The active field allows you to hide the category without removing it.")
    user_id = fields.Many2one('res.users', string="Assigned User")
    priority_id = fields.Many2one('website.support.ticket.priority', default=_default_priority_id, string="Priority")
