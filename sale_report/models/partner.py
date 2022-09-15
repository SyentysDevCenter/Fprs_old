from odoo import api, fields, models, _


class Partner(models.Model):
    _inherit = 'res.partner'

    modalite_paiement_id = fields.Many2one('modalite.paiement',string='Modalité de paiement')


