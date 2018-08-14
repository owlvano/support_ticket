{
    'name': "Горячая Линия",
    'version': "1.6.0",
    'author': "Ivan Sova / Sythil Tech",
    'category': "Tools",
    'support': "steven@sythiltech.com.au",
    'summary': "A helpdesk / support ticket system for your website (Odoo 10.0)",
    'description': "A helpdesk / support ticket system for your website but slightly modified",
    'website':'https://www.odoo.com/apps/modules/10.0/website_support/',
    'license':'LGPL-3',
    'data': [
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'views/website_support_ticket_views.xml',
        'views/website_support_ticket_subcategory_views.xml',
        'views/website_support_ticket_templates.xml',      
    ],
    'demo': [],
    'depends': ['mail','web', 'crm', 'website', 'website_support'],
    'installable': True,
}