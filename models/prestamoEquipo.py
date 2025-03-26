from odoo import models, fields

class PrestamoEquipo(models.Model):
    _name = 'prestamo.equipo'
    _description = 'Registro de equipos en préstamo'

    name = fields.Char(string='Nombre del Equipo', required=True)
    product_id = fields.Many2one('product.product', string='Producto Asociado', help="Producto que se gestiona en inventario")
    
    
from odoo import models, fields, api

class LoanEquipment(models.Model):
    _name = 'loan.equipment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Registro de Préstamos de Equipos'

    name = fields.Char("Nombre", required=True)
    product_id = fields.Many2one('product.product', string="Producto", required=True)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('loaned', 'Prestado'),
        ('returned', 'Devuelto')
    ], default='draft', tracking=True)
    picking_id = fields.Many2one('stock.picking', string="Movimiento de Inventario")

    @api.model
    def create(self, vals):
        equipment = self.env['equipo.equipo'].browse(vals['equipment_id'])
        if equipment.state != 'disponible':
            raise ValidationError("El equipo no está disponible para ser reservado.")
        
        loan = super(Prestamos, self).create(vals)
        loan.state = 'prestado'
        loan._update_equipment_state()

        # Crear movimiento de salida de inventario
        picking = self.env['stock.picking'].create({
            'partner_id': self.env.user.partner_id.id,
            'picking_type_id': self.env.ref('stock.picking_type_out').id,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'location_dest_id': self.env.ref('stock.stock_location_customers').id,
            'move_lines': [(0, 0, {
                # Nota: Es recomendable que cada equipo esté asociado a un producto (product.product)
                # para utilizar correctamente la lógica de inventario. Si no lo tienes, considera agregar
                # un campo product_id en tu modelo de equipo o asignar un producto genérico.
                'product_id': equipment.id,  
                'name': equipment.name,
                'product_uom_qty': 1,
                'product_uom': equipment.uom_id.id if hasattr(equipment, 'uom_id') else False,
                'location_id': self.env.ref('stock.stock_location_stock').id,
                'location_dest_id': self.env.ref('stock.stock_location_customers').id,
            })]
        })
        loan.write({'picking_id': picking.id})
        picking.action_confirm()
        picking.action_assign()

        return loan


    def write(self, vals):
        res = super(LoanEquipment, self).write(vals)
        for record in self:
            # Si se cambia el estado a 'Devuelto', se genera el movimiento de retorno
            if 'state' in vals and vals.get('state') == 'returned':
                picking_return = self.env['stock.picking'].create({
                    'partner_id': self.env.user.partner_id.id,
                    # Se utiliza el tipo de movimiento de entrada configurado en Odoo (ver referencia: stock.picking_type_in)
                    'picking_type_id': self.env.ref('stock.picking_type_in').id,
                    # Ubicación de origen: cliente o zona de préstamo
                    'location_id': self.env.ref('stock.stock_location_customers').id,
                    # Ubicación de destino: almacén
                    'location_dest_id': self.env.ref('stock.stock_location_stock').id,
                    'move_lines': [(0, 0, {
                        'product_id': record.product_id.id,
                        'name': record.product_id.name,
                        'product_uom_qty': 1,  # Cantidad a mover; ajustar según necesidad
                        'product_uom': record.product_id.uom_id.id,
                        'location_id': self.env.ref('stock.stock_location_customers').id,
                        'location_dest_id': self.env.ref('stock.stock_location_stock').id,
                    })]
                })
                record.write({'picking_id': picking_return.id})
                picking_return.action_confirm()
                picking_return.action_assign()
        return res
