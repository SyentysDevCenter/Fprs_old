from odoo import api, fields, models, _


class ModalitePaiment(models.Model):
    _name = 'modalite.paiement'
    _description = 'Modalites de Payment'

    name = fields.Char(string='Modalité de paiement' , required=True)


