from odoo import api, fields, models, _
from odoo.fields import Date

class WebsiteSupportTicketReportWizard(models.TransientModel):
    _name = "website.support.ticket.report.wizard"
    _description = "Website Support Ticket Report Wizard"

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')

    def format_date(self, raw_date):
        return Date.from_string(raw_date).strftime("%d.%m.%Y")
        
    @api.multi
    def do_search(self):
        self.ensure_one()
        self.env['website.support.ticket.report'].init(self.date_from, self.date_to)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Support Ticket Report (%s - %s)') % (self.format_date(self.date_from), self.format_date(self.date_to)), 
            'res_model': 'website.support.ticket.report',
            'view_mode': 'pivot',
            'context': {'date_from': self.date_from, 'date_to': self.date_to},
            'target': 'main'
        }
