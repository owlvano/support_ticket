# -*- coding: utf-8 -*-
from odoo import api, fields, models

class WebsiteSupportTicket(models.Model):

    _inherit = "website.support.ticket"
    
    @api.onchange('sub_category_id')
    def _onchange_sub_category_id(self):
        self.user_id= self.sub_category_id.user_id

    @api.model
    def create(self, vals):
        new_id = super(WebsiteSupportTicket, self).create(vals)

        new_id.ticket_number = new_id.company_id.next_support_ticket_number

        #Add one to the next ticket number
        new_id.company_id.next_support_ticket_number += 1

        #Automatically assign a responsible user
        if new_id.sub_category_id.user_id:
            new_id.user_id = new_id.sub_category_id.user_id

        #Auto create contact if one with that email does not exist
        setting_auto_create_contact = self.env['ir.values'].get_default('website.support.settings', 'auto_create_contact')
        
        if setting_auto_create_contact and 'email' in vals:
            if self.env['res.partner'].search_count([('email','=',vals['email'])]) == 0:
                if 'person_name' in vals:
                    new_contact = self.env['res.partner'].create({'name':vals['person_name'], 'email': vals['email'], 'company_type': 'person'})
                else:
                    new_contact = self.env['res.partner'].create({'name':vals['email'], 'email': vals['email'], 'company_type': 'person'})
                    
                new_id.partner_id = new_contact.id
                    
        #(BACK COMPATABILITY) Fail safe if no template is selected, future versions will allow disabling email by removing template
        ticket_open_email_template = self.env['ir.model.data'].get_object('website_support', 'website_ticket_state_open').mail_template_id
        if ticket_open_email_template == False:
            ticket_open_email_template = self.env['ir.model.data'].sudo().get_object('website_support', 'support_ticket_new')
            ticket_open_email_template.send_mail(new_id.id, True)
        else:
            ticket_open_email_template.send_mail(new_id.id, True)

        #Send an email out to everyone in the category
        notification_template = self.env['ir.model.data'].sudo().get_object('website_support', 'new_support_ticket_category')
        support_ticket_menu = self.env['ir.model.data'].sudo().get_object('website_support', 'website_support_ticket_menu')
        support_ticket_action = self.env['ir.model.data'].sudo().get_object('website_support', 'website_support_ticket_action')
        
        for my_user in new_id.category.cat_user_ids:
            values = notification_template.generate_email(new_id.id)
            values['body_html'] = values['body_html'].replace("_ticket_url_", "web#id=" + str(new_id.id) + "&view_type=form&model=website.support.ticket&menu_id=" + str(support_ticket_menu.id) + "&action=" + str(support_ticket_action.id) ).replace("_user_name_",  my_user.partner_id.name)
            #values['body'] = values['body_html']
            values['email_to'] = my_user.partner_id.email
                        
            send_mail = self.env['mail.mail'].create(values)
            send_mail.send()
            
            #Remove the message from the chatter since this would bloat the communication history by a lot
            send_mail.mail_message_id.res_id = 0
            
        return new_id
   

class WebsiteSupportTicketSubCategories(models.Model):

    _inherit = "website.support.ticket.subcategory"
    user_id = fields.Many2one('res.users', string="Assigned User")