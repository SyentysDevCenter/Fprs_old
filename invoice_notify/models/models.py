# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError
import base64



class Company(models.Model):
    _inherit = 'res.company'

    personnes_ids = fields.Many2many('res.users', relation='invoice_attente_persone_rel', string='Notifier les personnes:Factures en attente')
    pesonnes2_ids = fields.Many2many('res.users', relation='invoice_valide_persone_rel', string='Notifier les personnes:Factures validées')



class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_en_attente(self):
        super(AccountMove, self).action_en_attente()
        for rec in self:
            vals = {'invoice_id': self.id}
            facture_attente = self.env['facture.en.attente'].search([('invoice_id', '=', self.id)])
            if facture_attente:
                facture_attente = facture_attente[0]
            else:
                facture_attente = self.env['facture.en.attente'].create(vals)

            users = rec.company_id.personnes_ids
            if users:
                for user in users:
                    facture_attente.activity_schedule('invoice_notify.facture_en_attente_activity',
                                              user_id=user.id)


    def action_post(self):
        res = super(AccountMove, self).action_post()
        for rec in self:
            if rec.company_id.pesonnes2_ids:
                template_id = self.env.ref('invoice_notify.email_template_facture_valide')

                if not template_id:
                    raise ValidationError(u'Il faut définir le modèle de mail de validation des factures')
                related_facture_attente = rec.env['facture.en.attente'].search([('invoice_id', '=', rec.id)], limit=1)
                users = rec.company_id.pesonnes2_ids
                if related_facture_attente:
                    existing_activity = rec.env['mail.activity'].search([('res_id', '=', related_facture_attente.id),('res_model_id', '=',rec.env.ref('invoice_notify.model_facture_en_attente').id)])
                    if existing_activity:
                        existing_activity.action_done()
                if users:
                    for user in users:
                        related_partner = user.partner_id
                        body_html = ((
                                "Bonjour Mr(Mme) %(name)s,\n" \
                                " la facture en pièce jointe a été validée.\n" \
                                "Cordialement"
                                % {
                                    'name': related_partner.name,
                                    'facture': rec.name
                                }))

                        email_values = {
                            'subject': template_id.subject,
                            'date': fields.Date.context_today(self),
                            'email_to': related_partner.email,
                            'body_html': body_html,
                            'email_from': self.env.ref('base.user_admin').email,

                        }
                        email_obj = template_id.send_mail(self.id, email_values=email_values, force_send=True)
        return res


class FactureEnAttente(models.Model):
    _name = 'facture.en.attente'
    _inherit = ['mail.thread', 'portal.mixin', 'mail.activity.mixin']
    _description = 'Factures en Attente'

    invoice_id = fields.Many2one('account.move', string='Facture')
    invoice_name = fields.Char(related='invoice_id.name', store=True)
    invoice_date = fields.Date(related='invoice_id.invoice_date', string='Date de facturation', store=True)
    invoice_partner = fields.Many2one(related='invoice_id.partner_id', store=True, string='Partenaire')
    invoice_state = fields.Selection(related='invoice_id.state', store=True)
    amount_total = fields.Monetary(related='invoice_id.amount_total', store=True)
    currency_id = fields.Many2one(related='invoice_id.currency_id', store=True)

    def open_invoice(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        form_view = [(self.env.ref('account.view_move_form').id, 'form')]
        if 'views' in action:
            action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
        else:
            action['views'] = form_view
        action['res_id'] = self.invoice_id.id
        action['domain'] = [('id', '=', self.invoice_id.id)]

        return action





