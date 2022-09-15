# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class BankCaution(models.Model):
    _name = 'bank.caution'
    _inherit = ['mail.thread','mail.activity.mixin']

    name = fields.Char('Nom')
    bank_id = fields.Many2one('res.bank', 'Banque')
    amount = fields.Float('Montant')
    line_ids = fields.One2many('bank.caution.line', 'caution_id', 'Lignes de caution')
    residual = fields.Float('Montant restant', compute='compute_residual', store=True,
                            help='Ce montant soustrait les cautions recupérés de la ligne de crédit')
    amount_unreserved = fields.Float(u'Montant non reservé', compute='compute_residual', store=True,
                                     help='Ce montant soustrait les cautions recupérées et demandées de la ligne de crédit')


    @api.depends('amount', 'line_ids', 'line_ids.amount', 'line_ids.state_id')
    def compute_residual(self):
        for rec in self:
            line_accord = rec.line_ids.filtered(lambda r: r.state_id == 'mainleve_recue')
            rec.residual = rec.amount - sum([l.amount for l in line_accord])
            line_reserve = rec.line_ids.filtered(lambda r: r.state_id != 'mainleve_recue')
            amount_reserved = sum([l.amount for l in line_reserve])
            # if amount_reserved > rec.amount:
            #     raise ValidationError(u'Les cautions réservées dépassent le montant accordé')
            rec.amount_unreserved = rec.amount - amount_reserved
        return True




class BankCautionLine(models.Model):
    _name = 'bank.caution.line'

    number = fields.Char(u'Numéro')
    name = fields.Char('Description', required=True)
    nature = fields.Selection([('provisoire', 'Provisoire'), ('definitive', u'Définitive'), ('rg', 'RG')], default='provisoire', string="Nature")
    amount = fields.Float('Montant')
    # state = fields.Selection([('draft', 'En cours'), ('arestitue', u'A restituer'),
    #                           ('litige', u'Litige'), ('restitue', u'Restituée'), ('non_parvenu', 'Resultat non parvenu')], default='draft', string="Etat")
    state_id = fields.Selection([('encours', 'Encours'), ('echue', 'Echue'),
                                 ('mainleve_depose', u'Mainlevée déposé'), ('mainleve_recue', u'Mainlevée reçue')], string='Etat',default='encours')
    caution_id = fields.Many2one('bank.caution', 'Caution')
    date = fields.Date('Date')
    type = fields.Selection([('ao', 'AO'), ('marche', 'Marché'), ('contrat', 'Contrat'), ('convention', 'Convention')], default='ao')
    note = fields.Text('Observations')
    organisme_id = fields.Many2one('res.partner', 'Organisme')
    zone = fields.Char()


def action_assign(self):
        self.write({'state': 'assign'})
        return True


def action_cancel(self):
        self.write({'state': 'cancel'})
        return True


def action_restitue(self):
        self.write({'state': 'restitue'})
        return True


