from odoo import api, fields, models
from odoo.fields import Datetime

class WebsiteSupportTicketReportWizard(models.TransientModel):
    _name = "website.support.ticket.report.wizard"
    _description = "Website Support Ticket Report Wizard"

    date_from = fields.Datetime('Date From')
    date_to = fields.Datetime('Date To')

    def format_date(self, raw_date):
        return Datetime.from_string(raw_date).strftime("%d.%m.%Y")
        
    @api.multi
    def do_search(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Support Ticket Report (%s - %s)' % (self.format_date(self.date_from), self.format_date(self.date_to)), 
            'res_model': 'website.support.ticket.report',
            'view_mode': 'pivot',
            'context': {'date_from': self.date_from, 'date_to': self.date_to},
            'target': 'main'
        }
