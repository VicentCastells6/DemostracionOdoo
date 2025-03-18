import random
from odoo import models, fields, api # type: ignore

class Demo(models.Model):
    _name = 'demo.demo'
    _description = 'Demo'

    name = fields.Char(string="Nombre")
    value = fields.Integer(string="Valor")
    value2 = fields.Float(compute='compute_field', string="Valor con IVA 21%", store=True)
    description = fields.Text(string="Description")
    image = fields.Binary(string="Imagen")
    tags = fields.Many2many('demo.tag', string="Características")
    color = fields.Integer(string="Color")

    def compute_field(self):
        for record in self:
            record.value2 = record.value * 1.21
    
class DemoTag(models.Model):
    _name = 'demo.tag'
    
    name = fields.Char(string="Name", required=True)
    color = fields.Integer(string="Color", default=lambda self: self._get_default_color())

    @api.model
    def create(self, vals):
        if 'color' not in vals or vals.get('color') == 0:
            vals['color'] = random.randint(1, 11)  # Colores de 1 a 11
        return super(DemoTag, self).create(vals)