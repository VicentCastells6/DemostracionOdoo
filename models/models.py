import random
from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Equipos(models.Model):
    _name = 'equipo.equipo'
    _description = 'Equipos de la empresa'

    name = fields.Char(string="Nombre")
    serialNumber = fields.Char(string="Nº de serie", required=True, index=True, copy=False, unique=True)
    purchaseDate = fields.Date(string="Fecha de compra")
    warranty = fields.Binary(string="Garantía")
    state = fields.Selection([
        ('disponible', 'Disponible'),
        ('prestado', 'Prestado'),
        ('reparacion', 'En reparación'),
        ('baja', 'Dado de baja')
    ], string="Estado", default='disponible')
    employee_id = fields.Many2one('res.partner', string="Responsable", required=True)
    description = fields.Text(string="Descripción")
    image = fields.Binary(string="Imagen")
    tags = fields.Many2many('equipo.tag', string="Características")
    color = fields.Integer(string="Color")
    
    @api.model
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
        ('prestado', 'Prestado'),
        ('devuelto', 'Devuelto'),
        ('retrasado', 'Retrasado')
    ], string="Estado", default='prestado')
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
            self._update_equipment_state(loan)

    def _update_equipment_state(self, loan):
        if loan.state in ['devuelto', 'retrasado']:
            loan.equipment_id.state = 'disponible'
        else:
            loan.equipment_id.state = 'prestado'

    @api.model
    def create(self, vals):
        loan = super(Prestamos, self).create(vals)
        self._update_equipment_state(loan)
        return loan

    def write(self, vals):
        res = super(Prestamos, self).write(vals)
        for loan in self:
            self._update_equipment_state(loan)
        return res

    def action_devolver(self):
        """
        Marca el préstamo como devuelto y actualiza el estado del equipo.
        """
        today = fields.Date.today()  
        for loan in self:
            loan.state = 'devuelto'
            if not loan.longTerm:
                if loan.returnDate and loan.returnDate < today:
                    loan.state = 'retrasado'
            self._update_equipment_state(loan)
    
    def action_cancelar_devolucion(self):
        """
        Cancela la devolución y devuelve el estado del préstamo a 'prestado'.
        También actualiza el estado del equipo asociado.
        """
        for loan in self:
            if loan.state in ['devuelto', 'retrasado']:
                loan.state = 'prestado'
                loan.returnDate = False
                if loan.equipment_id:
                    loan.equipment_id.state = 'prestado'
            
    @api.model
    def notification(self):
        loans = self.search([('state', '=', 'prestado')])
        for loan in loans:
            if not loan.longTerm and loan.returnDate and loan.returnDate - timedelta(days=2) <= fields.Date.today():
                employee = loan.employee_id
                employee.message_post(body="El préstamo del equipo %s está próximo a vencer" % loan.equipment_id.name)
            if not loan.longTerm and loan.returnDate and loan.returnDate < fields.Date.today():
                loan.state = 'retrasado'
                employee = loan.employee_id
                employee.message_post(body="El préstamo del equipo %s está retrasado" % loan.equipment_id.name)

