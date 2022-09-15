from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ActualisationPrix(models.TransientModel):
    _name = 'actualisation.prix.contrat'

    pourcentage = fields.Float(string="Pourcentage", required=True, help='négatif pour les remises et positif pour les augmentations')
    sale_contrat_id = fields.Many2one(comodel_name="sale.contract", string="Contart Client", required=False, )

    def actualise(self):
        # check input value
        if 0 <= abs(self.pourcentage) <= 100:
            # update prices and make log message
            contract = self.sale_contrat_id
            if self.pourcentage > 0:
                message = 'Augmentation de ' + str(self.pourcentage) + '% <ul>'
            else:
                message = 'Remise de ' + str(self.pourcentage) + '% <ul>'
            for contract_line in contract.line_ids:
                message = message + '<li>[' + str(contract_line.product_id.default_code) + ']' + str(
                        contract_line.product_id.name) + ' : ' + str(round(contract_line.price,2)) + ' &rarr; '
                contract_line.price = contract_line.price * (1 + (self.pourcentage / 100))
                message = message + str(round(contract_line.price,2)) + '</li>'
            message = message + '</ul>'

            contract.message_post(body=message)
            contract.set_contract_to_draft()
            contract.Validate_contract()
            return {
                'type': 'ir.actions.client',
                'tag' : 'reload',
            }
        else:
            raise ValidationError('Vous devez saisir une valeur entre -100 et 100 !')
