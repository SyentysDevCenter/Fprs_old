# -*- coding: utf-8 -*-

from odoo import api, fields, models


class HrDepartment(models.Model):
	_inherit = 'hr.department'

	plombier = fields.Boolean("Plombier")
	charge_affaire = fields.Boolean("Chargé d’affaires")


class HrEmployeeBase(models.AbstractModel):
	_inherit = 'hr.employee.base'

	plombier = fields.Boolean("Plombier", related="department_id.plombier", store=True)
	charge_affaire = fields.Boolean("Chargé d’affaires", related="department_id.charge_affaire", store=True)


class ResUsers(models.Model):
	_inherit = 'res.users'

	plombier = fields.Boolean(related='employee_id.plombier')
	charge_affaire = fields.Boolean(related='employee_id.charge_affaire')

