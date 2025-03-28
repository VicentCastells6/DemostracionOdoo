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
    picking_id = fields.Many2one('stock.picking', string="Movimiento de Inventario")
    # Nuevo campo para integrar con el módulo de inventario
    product_id = fields.Many2one('product.product', string="Producto", copy=False)


#! Acciones CRUD
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Validación para que no se repita el número de serie
            if 'serialNumber' in vals:
                existing_equipment = self.search([('serialNumber', '=', vals['serialNumber'])], limit=1)
                if existing_equipment:
                    raise ValidationError("Ya existe un equipo con ese número de serie.")
            # Si no se especifica un producto, se crea automáticamente uno
            if not vals.get('product_id'):
                product_vals = {
                    'name': vals.get('name'),
                    'default_code': vals.get('serialNumber'),
                    'type': 'consu',
                    # Activa el tracking de stock; puedes elegir 'lot' o 'serial' según tus necesidades
                    'tracking': 'serial',
                    'is_storable': True,
                    'sale_ok': False,
                    'purchase_ok': False,
                }
                product = self.env['product.product'].create(product_vals)
                vals['product_id'] = product.id
        records = super(Equipos, self).create(vals_list)
        # Añadir una unidad al stock de inventario
        for record in records:
            if record.product_id:
                self.env['stock.quant']._update_available_quantity(
                    record.product_id, self.env.ref('stock.stock_location_stock'), 1
                )
        return records

    def write(self, vals):
        # Si se actualiza el nombre o el número de serie, podrías sincronizar el producto asociado
        res = super(Equipos, self).write(vals)
        for record in self:
            product_vals = {}
            if 'name' in vals:
                product_vals['name'] = record.name
            if 'serialNumber' in vals:
                product_vals['default_code'] = record.serialNumber
            if product_vals and record.product_id:
                record.product_id.write(product_vals)

        return res
    
    def unlink(self):
        # Si se borra un equipo, también se borra el producto asociado
        for record in self:
            if record.product_id:
                record.product_id.unlink()
        return super(Equipos, self).unlink()
#! Acciones CRUD


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



#? Clase auxiliar para etiquetas de características
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
