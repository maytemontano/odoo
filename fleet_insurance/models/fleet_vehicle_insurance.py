# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)

class FleetVehicleInsuranceType(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'fleet.insurance.type'
    _description = "Tipos de Seguro Vehiculos"
   
    name = fields.Char("Titulo")      
    period = fields.Integer(string="Meses de cobertura", type='integer', default=12)
    days_to_notify = fields.Integer(string="Dias para notificar", type='integer', 
            help="Numero de dias de anticipacion con que se debe de notificar a los seguidores de esta poliza que la misma esta por expirar.")
   
class FleetVehicleInsurance(models.Model):
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _name = 'fleet.vehicle.insurance' 
    _description = "Polizas Seguro Vehiculos"
          
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('confirm', 'Confirmada'),
        ('cancel', 'Cancelada'),
        ('expired', 'Expirada')], 'Estado', default='draft', readonly=True,
        track_visibility="onchange",
        copy=False)        
    name = fields.Char("Referencia")  
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehiculo', required=True) 
    fleet_insurance_type_id = fields.Many2one('fleet.insurance.type', 'Tipo', required=True) 
    date_start = fields.Date('Fecha de inicio', required=True,
        default=fields.Date.today, help='Fecha de inicio de vigencia de esta Poliza')
    date_end = fields.Date('Fecha de Fin', help='Fecha de fin de vigencia de esta Poliza')
    days_to_notify = fields.Integer(string="Dias para notificar", type='integer', 
            help="Numero de dias de anticipacion con que se debe de notificar a los seguidores de esta poliza que la misma esta por expirar.")
    to_expire_notification_sent = fields.Boolean("Se ha enviado o no notificacion de Poliza por expirar", default=False) 
   
   
    @api.onchange('fleet_insurance_type_id')
    def _compute_odometer_total(self):
        for record in self:
            record.days_to_notify = record.fleet_insurance_type_id.days_to_notify
      
    @api.onchange('date_start','fleet_insurance_type_id' )
    def _compute_date_end(self):
        for record in self:
            if self.date_start and self.fleet_insurance_type_id:
                date_start_dt = fields.Datetime.from_string(self.date_start)                
                self.date_end = fields.Datetime.to_string(date_start_dt + relativedelta(months=+self.fleet_insurance_type_id.period))         
          
    # ----------------------------------------------------
    # Actions
    # ----------------------------------------------------    
    
    @api.multi
    def action_confirm(self):
        self.write({'state': 'confirm'})
            
    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})
        
    @api.multi
    def action_set_draft(self):
        self.write({'state': 'draft'})
        
    @api.multi
    def action_set_expire(self):
        self.write({'state': 'expired'})
        
    @api.multi
    def action_set_to_expire(self):
        """ Comprueba si alguna Poliza esta dentro
            del periodo en que se tiene que notificar 
            que esta a punto de expirar y envia email 
            a todos los seguidores del registro y prende
            la bandera to_expire_notification_sent para 
            que ya no continue enviando avisos de expiracion """ 
        ids = self.search([('state', '=', 'confirm'), ('to_expire_notification_sent', '=', False)])  
        for record in ids:  
            daysDiff = (record.date_end- datetime.now().date()).days      
            if daysDiff <= record.days_to_notify:      
                body=('Poliza de Seguro Vehicular %s expira en %s dias') % (record.name, daysDiff)
                record.message_post(body=body, subject=body, subtype="mail.mt_comment")
                record.write({'to_expire_notification_sent': True}) 
                _logger.info('Se ha enviado email notificacion expira poliza seguro %s [%s] en %s dias', (record.name,record.id,daysDiff, ) )  
                
    @api.model
    def action_cron_expire_insurance(self):  
        """ Metodo invocado directamente desde el Cron.
            Cambia estado de Poliza de seguro de 
            'confirm' a 'expired' cuando la fecha
            'date_end' ha pasado
        """     
        current_date = str(datetime.now().date())   
        # Records expirados
        records = self.search([('state', '=', 'confirm'), ('date_end', '<', current_date)])
        records.action_set_expire()
        
        # Envia notificaciones de Polizas por expirar
        self.action_set_to_expire()
        