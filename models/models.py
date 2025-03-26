import random
from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Equipos(models.Model):
    _name = 'equipo.equipo'
    _description = 'Equipos de la empresa'

    name = fields.Char(string="Nombre")
    serialNumber = fields.Char(string="Nº de serie", required=True, index=True, copy=False)
    purchaseDate = fields.Date(string="Fecha de compra")
    warranty = fields.Binary(string="Garantía")
    state = fields.Selection([
        ('disponible', 'Disponible'),
        ('prestado', 'Prestado'),
        ('reparacion', 'En reparación'),
        ('baja', 'Dado de baja')
    ], string="Estado", default='disponible', readonly=True)
    employee_id = fields.Many2one('res.partner', string="Responsable", required=True)
    description = fields.Text(string="Descripción")
    image = fields.Binary(string="Imagen")
    tags = fields.Many2many('equipo.tag', string="Características")
    color = fields.Integer(string="Color")
    
    @api.model_create_multi
    def create(self, vals):
        # Validación para asegurarse de que no se repita el serialNumber
        if 'serialNumber' in vals:
            existing_equipment = self.search([('serialNumber', '=', vals['serialNumber'])], limit=1)
            if existing_equipment:
                raise ValidationError("Ya existe un equipo con ese número de serie.")
        
        return super(Equipos, self).create(vals)

    def write(self, vals):
    # Validación para asegurarse de que no se repita el serialNumber al actualizar
        if 'serialNumber' in vals:
            existing_equipment = self.search([('serialNumber', '=', vals['serialNumber'])], limit=1)
            if existing_equipment and existing_equipment.id != self.id:
                raise ValidationError("Ya existe un equipo con ese número de serie.")

        return super(Equipos, self).write(vals)
    
    def action_dar_baja(self):
        if self.state == 'prestado':
            raise ValidationError("No se puede dar de baja un equipo que está prestado.")
        self.state = 'baja'
    
    def action_dar_alta(self):
        if self.state != 'baja':
            raise ValidationError("El equipo no está dado de baja.")
        if self.state == 'prestado':
            raise ValidationError("No se puede dar de alta un equipo que está prestado.")
        self.state = 'disponible'

class EquipoTag(models.Model):
    _name = 'equipo.tag'
    _description = 'Tag'

    name = fields.Char(string="Nombre", required=True)
    color = fields.Integer(string="Color", default=lambda self: self._get_default_color())

    @api.model
    def create(self, vals):
        if 'color' not in vals or vals.get('color') == 0:
            vals['color'] = random.randint(1, 11)
        return super(EquipoTag, self).create(vals)
    
    def _get_default_color(self):
        return random.randint(1, 11)



