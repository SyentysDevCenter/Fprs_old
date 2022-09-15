# -*- coding: utf-8 -*-

from odoo import api, fields, models
import locale
import datetime

class ResCompany(models.Model):
	_inherit = 'res.company'

	devis_text_1 = fields.Html('Texte devis régul')
	devis_text_2 = fields.Html('Texte du devis 2')
	signature = fields.Binary('Signature de la présidente', help = 'Signature', copy = False,
							  attachment = True)

class ResUsers(models.Model):
	_inherit = 'res.users'

	signature = fields.Binary('Signature', help = 'Signature', copy = False,
							  attachment = True)


