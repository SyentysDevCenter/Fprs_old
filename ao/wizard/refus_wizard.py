# -*- coding: utf-8 -*-
import datetime
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AoRefusWizard(models.TransientModel):
    _name = "ao.refus.wizard"

    motif = fields.Text('Motif')
    date = fields.Date('Date')

    def validate(self):
        self.ensure_one()
        ao_id = self.env['ao.ao'].browse(self.env.context['active_id'])
        ao_id.motif_refus = self.motif
        ao_id.date_refus = self.date
        ao_id.state = 'refus'
        return True