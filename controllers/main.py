# -*- coding: utf-8 -*-
import odoo.http as http
from odoo.http import request

class SupportTicketController(http.Controller):
    @http.route('/support/subcategories/fetch', type='http', auth="public", website=True)
    def support_subcategories_fetch(self, **kwargs):

        values = {}
	for field_name, field_value in kwargs.items():
	    values[field_name] = field_value
	            
	sub_categories = request.env['website.support.ticket.subcategory'].sudo().search([('parent_category_id','=', int(values['category']) )])
	
	#Only return a dropdown if this category has subcategories
	return_string = ""
	
	if sub_categories:
	    return_string += "<div class=\"form-group\">\n"
	    return_string += u"    <label class=\"col-md-3 col-sm-4 control-label\" for=\"subcategory\">Подкатегория</label>\n"
	    return_string += "    <div class=\"col-md-7 col-sm-8\">\n"

            return_string += "        <select class=\"form-control\" id=\"subcategory\" name=\"subcategory\">\n"
            for sub_category in request.env['website.support.ticket.subcategory'].sudo().search([('parent_category_id','=', int(values['category']) )]):
                return_string += "            <option value=\"" + str(sub_category.id) + "\">" + sub_category.name + "</option>\n"

            return_string += "        </select>\n"
	    return_string += "    </div>\n"
            return_string += "</div>\n"
            
        return return_string