from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Prestamos(models.Model):
    _name = 'equipo.prestamo'
    _description = 'Préstamos de equipos'

    name = fields.Char(string="Nombre")
    employee_id = fields.Many2one('res.partner', string="Empleado", required=True)
    equipment_id = fields.Many2one('equipo.equipo', string="Equipo", required=True)
    longTerm = fields.Boolean(string="Préstamo a largo plazo", default=False)
    loanDate = fields.Date(string="Fecha de préstamo", required=True)
    returnDate = fields.Date(string="Fecha de devolución", compute='_compute_returnDate', store=True)
    state = fields.Selection([
        ('disponible', 'Disponible'),
        ('prestado', 'Prestado'),
        ('devuelto', 'Devuelto'),
        ('retrasado', 'Retrasado')
    ], string="Estado", default='disponible')
    description = fields.Text(string="Descripción")
    image = fields.Binary(string="Imagen", related='equipment_id.image', readonly=True)
    tags = fields.Many2many('equipo.tag', string="Características", related='equipment_id.tags', readonly=True)
    color = fields.Integer(string="Color", related='equipment_id.color', readonly=True)
        
    
    @api.depends('loanDate', 'longTerm')
    def _compute_returnDate(self):
        for loan in self:
            if loan.loanDate and not loan.longTerm:
                loan.returnDate = loan.loanDate + timedelta(days=7)
            else:
                loan.returnDate = False
    
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
                loan.state = 'disponible'
        self._update_equipment_state()

    @api.depends('state')
    def compute_visibility(self):
        for loan in self:
            loan.visibility = loan.state not in ['prestado', 'disponible']

    def _update_equipment_state(self):
        for loan in self:
            if loan.state in ['devuelto', 'retrasado']:
                loan.equipment_id.state = 'disponible'
            else:
                loan.equipment_id.state = 'prestado'

    @api.model
    def create(self, vals):
        equipment = self.env['equipo.equipo'].browse(vals['equipment_id'])
        if equipment.state != 'disponible':
            raise ValidationError("El equipo no está disponible para ser reservado.")
        
        loan = super(Prestamos, self).create(vals)
        loan.state = 'prestado'
        loan._update_equipment_state()
        return loan

    def write(self, vals):
        for loan in self:
            if 'equipment_id' in vals:
                equipment = self.env['equipo.equipo'].browse(vals['equipment_id'])
                if equipment.exists() and equipment.state != 'disponible':
                    raise ValidationError("El equipo no está disponible para ser reservado.")
            
            if 'state' in vals and vals['state'] == 'disponible':
                vals['state'] = 'prestado'
        
        res = super(Prestamos, self).write(vals)
        self._update_equipment_state()
        return res

    def action_devolver(self):
        today = fields.Date.today()  
        for loan in self:
            # Si el préstamo ya está devuelto (y no es a largo plazo), se lanza el error
            if loan.state == 'devuelto' and not loan.longTerm:
                raise ValidationError("El equipo ya ha sido devuelto.")
            
            # Para préstamos a largo plazo se marca como devuelto sin cambiar a retrasado
            if loan.longTerm:
                loan.state = 'devuelto'
            else:
                # Para préstamos no a largo plazo, se marca como devuelto o retrasado según la fecha de devolución
                loan.state = 'devuelto'
                if loan.returnDate and loan.returnDate < today:
                    loan.state = 'retrasado'
                    
            loan._update_equipment_state()

    def action_cancelar_devolucion(self):
        for loan in self:
            # Verificar si el equipo está prestado en otro préstamo
            other_loans = self.search([('equipment_id', '=', loan.equipment_id.id), ('state', '=', 'prestado')])
            if other_loans:
                raise ValidationError(f"El equipo {loan.equipment_id.display_name} está actualmente prestado en otro préstamo y no se puede cancelar la devolución.")
            
            if loan.state in ['devuelto', 'retrasado']:
                loan.state = 'prestado'
                loan.returnDate = False
                loan.equipment_id.state = 'prestado'

            
    @api.model
    def notification(self):
        today = fields.Date.today()
        loans = self.search([('state', '=', 'prestado')])
        for loan in loans:
            if not loan.longTerm and loan.returnDate:
                if loan.returnDate - timedelta(days=2) <= today:
                    loan.employee_id.message_post(body=f"El préstamo del equipo {loan.equipment_id.name} está próximo a vencer.")
                if loan.returnDate < today:
                    loan.state = 'retrasado'
                    loan.employee_id.message_post(body=f"El préstamo del equipo {loan.equipment_id.name} está retrasado.")