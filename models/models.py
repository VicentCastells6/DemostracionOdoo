# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Demo(models.Model):
    _name = 'demo.demo'
    _description = 'demo.demo'

    name = fields.Char(string="Name")
    value = fields.Integer(string="Value")
    value2 = fields.Float(compute="_value_pc", store=True, string="Value Percentage")
    description = fields.Text(string="Description")
    active = fields.Boolean(string="Active", default=True)
    image = fields.Image('Image', max_width=128, max_height=128)

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100

