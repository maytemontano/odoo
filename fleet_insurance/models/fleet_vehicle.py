# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class Fleet(models.Model): 
    _inherit = 'fleet.vehicle'
    
    insurance_count = fields.Integer(compute="_compute_insurance_count", string='Seguros')
    
    def _compute_insurance_count(self):
        Insurance = self.env['fleet.vehicle.insurance']
        for record in self:
            record.insurance_count = Insurance.search_count([('vehicle_id', '=', record.id), ('state', '=', 'confirm')])   
            
    # ----------------------------------------------------
    # Actions
    # ----------------------------------------------------    
            
    @api.multi
    def return_action_to_open_fleet_insurance(self):
        """ This opens the xml view specified in xml_id for the current vehicle """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window'].for_xml_id('fleet_insurance', xml_id)
            res.update(
                context=dict(self.env.context, default_vehicle_id=self.id, group_by=False),
                domain=[('vehicle_id', '=', self.id), ('state', '=', 'confirm')]
            )
            return res
        return False
            