# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Prueba(models.Model):
    _name = 'prueba.prueba'
    _description = 'prueba.prueba'

    name = fields.Char(string="Name")
    value = fields.Integer(string="Value")
    value2 = fields.Float(compute="_value_pc", store=True, string="Value Percentage")
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active", default=True)

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100

