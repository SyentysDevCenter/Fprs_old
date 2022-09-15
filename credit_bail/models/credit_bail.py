from odoo import api, fields, models
from dateutil.relativedelta import relativedelta
from datetime import date


class CreditBail(models.Model):
    _name = 'account.credit.bail'
    _inherit = ['mail.thread', 'mail.activity.mixin',]


    name = fields.Char(string="Titre", required=False, states={'draft': [('readonly', False)]}, readonly=1, tracking=True)
    state = fields.Selection([('draft', 'Nouveau'), ('validate', 'Validé'), ('cancel', 'Annulé'), ('done', 'Terminé')], string='Status', default='draft', index=True, tracking=True)
    nombre_de_mois = fields.Integer(string="Nombre de mois", required=True, states={'draft': [('readonly', False)]}, readonly=1, tracking=True)
    montant = fields.Float(string="Montant",  required=True, states={'draft': [('readonly', False)]}, readonly=1, tracking=True)
    date_premiere_operation = fields.Date(string="Date première opération", required=True, states={'draft': [('readonly', False)]}, readonly=1, tracking=True)
    date_limite = fields.Date(string="Date limite", compute='compute_date_limite', states={'draft': [('readonly', False)]}, readonly=1, tracking=True)
    company_id = fields.Many2one('res.company', string='Société', required=True, index=True, default=lambda self: self.env.company, states={'draft': [('readonly', False)]}, readonly=1, tracking=True)
    journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", required=True, states={'draft': [('readonly', False)]}, readonly=1, tracking=True)
    account_income_id = fields.Many2one(comodel_name="account.account", string="Compte de revenus", required=True, states={'draft': [('readonly', False)]}, readonly=1, tracking=True)
    account_bank_id = fields.Many2one(comodel_name="account.account", string="Compte de banque", required=True, states={'draft': [('readonly', False)]}, readonly=1, tracking=True)
    project_id = fields.Many2one(comodel_name="project.project", string="code chantier", required=False, states={'draft': [('readonly', False)]}, readonly=1, tracking=True)

    account_move_ids = fields.One2many(comodel_name="account.move", inverse_name="credit_bail_id", string="Pièces comptables", required=False)
    date_prochaine_operation = fields.Date(string="Date prochaine opération", readonly=1, tracking=True)

    @api.depends('date_premiere_operation', 'nombre_de_mois')
    def compute_date_limite(self):
        for rec in self:
            if rec.date_premiere_operation:
                rec.date_limite = rec.date_premiere_operation + relativedelta(months=+rec.nombre_de_mois)
            else:
                rec.date_limite = False

    # display account move
    def get_account_move(self):
        return {
            'name': 'Pièces comptables',
            'view_mode': 'tree,form',
            'view_id': False,
            'res_model': 'account.move',
            'domain': [('credit_bail_id.id', '=', self.id)],
            'type': 'ir.actions.act_window'
        }

    def validate(self):
        self.ensure_one()
        self.state = 'validate'
        self.date_prochaine_operation = self.date_premiere_operation

    def action_cancel(self):
        self.write({'state' : 'cancel'})

    # cron job method
    def create_account_move(self):
        credit_bail = self.env['account.credit.bail'].search([('date_prochaine_operation', '<=', date.today()), ('state', '=', 'validate')])

        for rec in credit_bail:
            if rec.date_prochaine_operation < date.today():
                date_suivant = rec.date_prochaine_operation
                while date_suivant < date.today() and len(rec.account_move_ids) != rec.nombre_de_mois:
                    if date_suivant >= rec.date_premiere_operation:
                        account_move =self.new_account_move(rec, date_suivant)
                        account_move.action_post()
                    date_suivant = date_suivant + relativedelta(months=+1)
                rec.date_prochaine_operation = date_suivant
            else:
                account_move = self.new_account_move(rec, rec.date_prochaine_operation)
                account_move.action_post()
                rec.date_prochaine_operation = rec.date_prochaine_operation + relativedelta(months=+1)

            if len(rec.account_move_ids) == rec.nombre_de_mois:
                rec.state = 'done'
                rec.date_prochaine_operation = False

    # create new account move
    def new_account_move(self, credit_bail, date):
        return self.env['account.move'].create({
                'ref': f'CB : {credit_bail.name} {date}',
                'sale_chantier_id': credit_bail.project_id.id if credit_bail.project_id else False,
                'date': date,
            'company_id': credit_bail.company_id.id,
                'credit_bail_id': credit_bail.id,
                'journal_id': credit_bail.journal_id.id,
                'line_ids': [(0, 0, {'account_id': credit_bail.account_income_id.id, 'debit': credit_bail.montant, 'name':credit_bail.name}),
                             (0, 0, {'account_id': credit_bail.account_bank_id.id, 'credit': credit_bail.montant, 'name':credit_bail.name})],
            })
