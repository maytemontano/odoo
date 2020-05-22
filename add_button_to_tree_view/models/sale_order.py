# -*- coding: utf-8 -*-

from odoo.exceptions import UserError
from odoo import models

class SaleOrder(models.Model):
    _inherit = 'sale.order'    

    def js_sale_order_custom_button(self):        
        """ Method called from JS custom button "My Custom Button" """
        raise UserError("Message from your custom Sale Order Button!")
