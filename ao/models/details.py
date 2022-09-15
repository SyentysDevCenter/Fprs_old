# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class VisiteLieux(models.Model):
    _inherit = 'visite.lieu'

    ao_id = fields.Many2one('ao.ao', "AO", ondelete='cascade')


class Ville(models.Model):
    _name = "ao.ville"
    _description = "Ville"

    name = fields.Char("Ville", required=True)


class AoAgreement(models.Model):
    _name = "ao.agreement"

    name = fields.Char('Nom', required=True)


class AoPrestation(models.Model):
    _name = "ao.prestation"

    name = fields.Char("Prestation", required=True)


# class ReglementAo(models.Model):
#     _name = "ao.reglement"
#     _description = "Reglement AO"
#
#     ao_id = fields.Many2one("ao.ao", "AO", ondelete='cascade')
#     name = fields.Char(String="Description", required=True)
#     critere_id = fields.Many2one("ao.reglement.critere", string=u"Critère")
#     date = fields.Date(string=u'Date limite de réponse')
#     resp_id = fields.Many2one('res.users', string='Responsable', track_visibility='onchange')
#     cible = fields.Selection([('caution', 'Caution'),
#                               ('offre_tech', 'Offre technique'),
#                               ('dossier_tech', 'Dossier technique & administratif'),
#                               ('offre_financiere', u'Offre financière'),
#                               ('clause_particuliere', u'Clauses particulières')],
#                              string=u"Elément cible")
#     state = fields.Selection([('draft', 'Nouveau'), ('done', u'Validé')], default='draft', string="Etat")
#
#     @api.onchange('name', 'cible')
#     def _check_name(self):
#         for record in self:
#             if record.cible == 'caution':
#                 if not self.isfloat(self.name):
#                     raise ValidationError(u"Dans le cas d'une caution, veuillez saisir un montant dans la desription! \n"
#                                           u"Pour saisir un nombre décimal, utilisez un point au lieu de la virgule.")
#
#     def isfloat(self, value):
#         try:
#             float(value)
#             return True
#         except:
#             return False
#
#
#     def button_confirme(self):
#         self.write({'state': 'done' })
#         return True
#

# class CritereReglement(models.Model):
#     _name = "ao.reglement.critere"
#     _description = u"Critère de reglement AO"
#
#     name = fields.Char(string=u"Critère", required=True)


class LivrableDemande(models.Model):
    _name = "ao.livrable.demande"
    _description = "Livrables AO"

    ao_id = fields.Many2one('ao.ao', "AO", ondelete='cascade')
    name = fields.Char(string="Description", required=True)
    date_echeance = fields.Date(u"Date échéance")
    date_realisation = fields.Date(string=u"Date réalisation")
    attachment_ids = fields.Many2many("ir.attachment",
                                      "ao_livrable_rel",
                                      "livrable_id",
                                      "attach_id",
                                      string="Fichiers")


class AoIntervenant(models.Model):
    _name = "ao.intervenant"
    _description = "Intervenant AO"

    ao_id = fields.Many2one('ao.ao', "AO", ondelete='cascade')
    name = fields.Char("Intervenant", required=True)


# class AoOrganisme(models.Model):
#     _name = "ao.organisme"
#     _description = "Organisme AO"
#
#     name = fields.Char("Organisme", required=True)


class AoChecklist(models.Model):
    _name = "ao.checklist"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Checklist de l'AO"
    _order = 'sequence'

    sequence = fields.Char(u'Séquence')
    numero = fields.Integer(u'Numéro', default=1)
    cible = fields.Selection([('dossier_tech', 'Dossier technique'),
                              ('dossier_admin', 'Dossier administratif'),
                              ('dossier_additif', u'Dossier additif'),
                              ('cps_signe', u'CPS signé'),
                              ('offre_tech', 'Offre technique'),
                              ('offre_financiere', u'Offre financière'),
                              ('clause_particuliere', u'Clause particulière'),
                              ('autre', u'Autres'),
                              ],
                             string=u"Elément cible")
    type_document_id = fields.Many2one('dossier.type.document', 'Type de document')
    desc = fields.Text("Description", required=True)
    enveloppe_id = fields.Many2one('ao.enveloppe', "Enveloppe")
    resp_id = fields.Many2one('res.partner', string='Responsable')
    date_echeance = fields.Date(u"Date échéance", required=True)
    date_realisation = fields.Date(u"Date réalisation", related='dossier_line.date_realisation', readonly=True, store=True)
    # etat = fields.Boolean(u'Validé')
    dossier_line = fields.Many2one('ao.dossier', string='Document')
    ao_id = fields.Many2one('ao.ao', "AO", required=True, ondelete='cascade')

    @api.model
    def create(self, vals):
        res = super(AoChecklist, self).create(vals)
        if vals.get('resp_id', False):
            template_id = self.env.ref("ao.email_template_checklist_resp")

            # message_follower_ids =  ${str.join(', ', object.intervenant_ids.mapped('name'))}

            res.message_subscribe([res.resp_id.id])
            res.message_post_with_template(template_id=template_id.id,)
                                             # message_type='email')
        return res

    def write(self, vals):
        res = super(AoChecklist, self).write(vals)
        if vals.get('resp_id', False):
            template_id = self.env.ref("ao.email_template_checklist_resp")

            # message_follower_ids =  ${str.join(', ', object.intervenant_ids.mapped('name'))}
            for rec in self:
                rec.message_subscribe([rec.resp_id.id])
                rec.message_post_with_template(template_id=template_id.id,)
                                             # message_type='email')
        return res


    def button_confirme(self):
        name = ''
        if self.type_document_id:
            name = self.type_document_id.name
        name += '/'+ self.desc
        vals = {
            'sequence': self.sequence,
            # 'numero': self.numero,
            'name': name,
            'resp': self.resp_id.id,
            'enveloppe_id': self.enveloppe_id.id,
            'echeance': self.date_echeance,
            'date_realisation': self.date_realisation
        }
        if not self.cible:
            raise ValidationError(u"Veuillez choisir un élément cible!")

        if self.cible == 'offre_tech':
            vals['ao_tech'] = self.ao_id.id
        if self.cible == 'cps_signe':
            vals['ao_cps_signe'] = self.ao_id.id

        if self.cible == 'dossier_tech':
            vals['dossier_tech'] = self.ao_id.id
        if self.cible == 'dossier_admin':
            vals['ao_dossier_admin'] = self.ao_id.id

        if self.cible == 'offre_financiere':
            vals['ao_financier'] = self.ao_id.id
        if self.cible == 'dossier_additif':
            vals['dossier_add_id'] = self.ao_id.id
        if self.cible == 'clause_particuliere':
            vals['ao_clause_particuliere'] = self.ao_id.id
        if self.cible == 'autre':
            vals['ao_autre_dossier'] = self.ao_id.id

        dossier_id = self.env['ao.dossier'].create(vals)
        # self.etat = True
        self.dossier_line = dossier_id.id
        return True

class aoEnvelloppe(models.Model):
    _name = 'ao.enveloppe'

    name = fields.Char('Enveloppe', required=True)


class AoCpsChange(models.Model):
    _name = "ao.cps.change"
    _description = "Changement du CPS des appels d'offre"
    _order = 'date desc'

    name = fields.Char('Remarque', required=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    attachment_ids = fields.Many2many("ir.attachment",
                                      "ao_cps_change_rel",
                                      "cps_id",
                                      "attach_id",
                                      string="Fichiers")
    ao_id = fields.Many2one('ao.ao', "Appel d'offre")


class Caution(models.Model):
    _inherit = 'bank.caution.line'

    ao_id = fields.Many2one('ao.ao', 'Ao')
