from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Prestamos(models.Model):
    _name = 'equipo.prestamo'
    _description = 'Préstamos de equipos'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre")
    employee_id = fields.Many2one('res.partner', string="Empleado", required=True)
    equipment_id = fields.Many2one('equipo.equipo', string="Equipo", required=True)
    longTerm = fields.Boolean(string="Préstamo a largo plazo", default=False)
    loanDate = fields.Date(string="Fecha de préstamo", required=True)
    returnDate = fields.Date(string="Fecha de devolución", compute='_compute_returnDate', store=True)
    state = fields.Selection([
        ('borrador', 'Borrador'),
        ('espera_aprobacion', 'Espera'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('prestado', 'Prestado'),
        ('devuelto', 'Devuelto'),
        ('retrasado', 'Retrasado')
    ], string="Estado", default='borrador', )
    description = fields.Text(string="Descripción")
    image = fields.Binary(string="Imagen", related='equipment_id.image', readonly=True)
    tags = fields.Many2many('equipo.tag', string="Características", related='equipment_id.tags', readonly=True)
    color = fields.Integer(string="Color", related='equipment_id.color', readonly=True)
    picking_id = fields.Many2one('stock.picking', string="Movimiento de Inventario")
    calendar_return_date = fields.Date(
    string="Fecha fin calendario",
    compute="_compute_calendar_return_date",
    store=True
    )
    approved_by = fields.Many2one('res.users', string="Aprobado por", readonly=True)
    approved_date = fields.Datetime(string="Fecha de aprobación", readonly=True)
    notified = fields.Boolean(string="Notificado", default=False)



    # longTerm: True -> returnDate: False
    @api.depends('returnDate', 'loanDate', 'longTerm')
    def _compute_calendar_return_date(self):
        for record in self:
            if record.returnDate:
                record.calendar_return_date = record.returnDate
            elif record.longTerm and record.loanDate:
                # Mostrar como evento de un solo día si es indefinido
                record.calendar_return_date = record.loanDate
            else:
                record.calendar_return_date = record.returnDate or record.loanDate

    # Cambio de stock en inventario al crear o devolver un préstamo
    def _update_stock(self, product, quantity_change):
        """Actualiza el stock disponible en inventario."""
        try:
            if not product:
                raise ValidationError("El equipo no tiene un producto asociado.")
            location = self.env.ref('stock.stock_location_stock')
            if not location:
                raise ValidationError("No se encontró la ubicación de inventario.")
            self.env['stock.quant']._update_available_quantity(product, location, quantity_change)
        except Exception as e:
            raise ValidationError(f"Ocurrió un error al actualizar el inventario: {str(e)}")


    # returnDate = loanDate + 7 si no es a largo plazo   
    @api.depends('loanDate', 'longTerm')
    def _compute_returnDate(self):
        for loan in self:
            if loan.loanDate and not loan.longTerm:
                loan.returnDate = loan.loanDate + timedelta(days=7)
            else:
                loan.returnDate = False
                
    # Estado del préstamo
    @api.depends('loanDate', 'returnDate', 'longTerm')
    def _compute_state(self):
        for loan in self:
            if loan.longTerm:
                loan.state = 'prestado'
            elif loan.returnDate and loan.returnDate < fields.Date.today() and loan.state == 'prestado':
                loan.state = 'retrasado'
            elif loan.returnDate and loan.returnDate >= fields.Date.today() and loan.state == 'prestado':
                loan.state = 'prestado'
            elif not loan.returnDate and not loan.loanDate:
                loan.state = 'borrador'
        self._update_equipment_state()


    # Actualizar estado del equipo
    def _update_equipment_state(self):
        for loan in self:
            if loan.state in ['prestado', 'aprobado']:
                loan.equipment_id.state = 'prestado'
            else:
                loan.equipment_id.state = 'disponible'



    @api.model
    def create(self, vals):
        equipment = self.env['equipo.equipo'].browse(vals['equipment_id'])

        if equipment.state != 'disponible':
            raise ValidationError("El equipo no está disponible para ser reservado.")

        product = equipment.product_id
        if not product or not product.is_storable:
            raise ValidationError("El equipo no tiene un producto almacenable asignado.")

        loan = super(Prestamos, self).create(vals)

        
        loan.message_post(body="Préstamo creado y pendiente de aprobación.")
        return loan




    def write(self, vals):
        for loan in self:
            if 'equipment_id' in vals:
                equipment = self.env['equipo.equipo'].browse(vals['equipment_id'])
                if equipment.exists() and (equipment.state != 'disponible' or equipment.state != 'aprobado'):
                    raise ValidationError("El equipo no está disponible para ser reservado.")

        res = super(Prestamos, self).write(vals)
        self._update_equipment_state()
        return res


    #* Comportamiento de botones 
    def action_solicitar_aprobacion(self):
        for loan in self:
            if loan.state != 'borrador':
                raise ValidationError("Solo los préstamos en borrador pueden ser enviados para aprobación.")
            loan.state = 'espera_aprobacion'
            loan.message_post(body="Solicitud de préstamo enviada para aprobación.")



    def action_aprobar(self):
        if not self.env.user.has_group('stock.group_stock_manager'):
            raise ValidationError("No tienes permisos para aprobar préstamos.")
            
        for loan in self:
            if loan.state not in ['espera_aprobacion', 'rechazado']:
                raise ValidationError("Solo se pueden aprobar solicitudes en estado 'Espera'.")
            loan.state = 'aprobado'
            loan.approved_by = self.env.user
            loan.approved_date = fields.Datetime.now()
            loan.message_post(body="Solicitud de préstamo aprobada. Aún no se ha prestado el equipo.")


    def action_rechazar(self):
        if not self.env.user.has_group('stock.group_stock_manager'):
            raise ValidationError("No tienes permisos para rechazar préstamos.")
            
        for loan in self:
            if loan.state not in ['espera_aprobacion', 'aprobado']:
                raise ValidationError("Solo se pueden rechazar solicitudes en estado 'Espera' o 'Aprobado'.")
            loan.state = 'rechazado'
            loan.message_post(body="Solicitud de préstamo rechazada.")


    def action_prestar(self):
        for loan in self:
            if loan.state != 'aprobado':
                raise ValidationError("Solo se pueden prestar solicitudes aprobadas.")

            product = loan.equipment_id.product_id
            if not product or not product.is_storable:
                raise ValidationError("El equipo no tiene un producto almacenable asignado.")

            loan.state = 'prestado'
            loan._update_equipment_state()
            loan._update_stock(product, -1)
            loan.message_post(body="El préstamo ha sido procesado y el equipo fue entregado.")


    def action_devolver(self):
        today = fields.Date.today()  
        for loan in self:
            if loan.state == 'devuelto' and not loan.longTerm:
                raise ValidationError("El equipo ya ha sido devuelto.")
            
            product = loan.equipment_id.product_id
            if not product or not product.is_storable:
                raise ValidationError("El equipo no tiene un producto almacenable asignado.")


            # Estado
            if loan.longTerm:
                loan.state = 'devuelto'
            else:
                loan.state = 'devuelto'
                if loan.returnDate and loan.returnDate < today:
                    loan.state = 'retrasado'

            loan._update_equipment_state()

            # Sumar 1 al stock si hay producto
            if loan.equipment_id.product_id:
                loan._update_stock(loan.equipment_id.product_id, 1)
            loan.message_post(body="Equipo devuelto.")


    def action_cancelar_devolucion(self):
        for loan in self:
            other_loans = self.search([('equipment_id', '=', loan.equipment_id.id), ('state', '=', 'prestado')])
            if other_loans:
                raise ValidationError(f"El equipo {loan.equipment_id.display_name} está actualmente prestado en otro préstamo y no se puede cancelar la devolución.")
            
            if loan.state in ['devuelto', 'retrasado']:
                loan.state = 'prestado'
                loan.returnDate = False
                loan.equipment_id.state = 'prestado'

                # Volver a restar 1 al stock
                if loan.equipment_id.product_id:
                    loan._update_stock(loan.equipment_id.product_id, -1)


            
    @api.model
    def notification(self):
        today = fields.Date.today()
        loans = self.search([
            ('state', '=', 'prestado'),
            ('longTerm', '=', False),
            ('returnDate', '!=', False)
        ])
        
        for loan in loans:
            user = loan.employee_id.user_id
            if not user:
                continue  

            if loan.returnDate - timedelta(days=2) <= today and not loan.notified:
                loan.message_post(
                    body=f"📅 <b>Préstamo próximo a vencer:</b> El equipo <i>{loan.equipment_id.name}</i> vence el {loan.returnDate}.",
                    message_type='comment',
                )
                loan.notified = True

            if loan.returnDate < today and loan.state != 'retrasado':
                loan.state = 'retrasado'
                loan.message_post(
                    body=f"⚠️ <b>Préstamo retrasado:</b> El equipo <i>{loan.equipment_id.name}</i> tenía fecha de devolución el {loan.returnDate}.",
                    message_type='comment',
                )

