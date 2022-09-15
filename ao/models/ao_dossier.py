# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Dossier(models.Model):
    _name = "ao.dossier"
    _description = 'Dossier'
    _rec_name = 'complete_name'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence'

    sequence = fields.Char(u'Sequence')
    numero = fields.Integer(u'Numéro', default=1)
    complete_name = fields.Char(compute='get_complete_name', string='Nom', store=True)
    name = fields.Text("Description", required=True, track_visibility='onchange')
    resp = fields.Many2one('res.partner', 'Responsable', track_visibility='onchange')
    echeance = fields.Date(u"Date d'echéance", track_visibility='onchange')
    attachment_ids = fields.Many2many("ir.attachment",
                                      "ao_dossier_rel",
                                      "dossier_id",
                                      "attach_id",
                                      string="Fichiers",track_visibility='onchange')
    enveloppe_id = fields.Many2one('ao.enveloppe', "Enveloppe", invisible=True)
    ao_tech = fields.Many2one('ao.ao', "AO", invisible=True)
    dossier_tech = fields.Many2one('ao.ao', "AO", invisible=True)
    ao_dossier_admin = fields.Many2one('ao.ao', "AO", invisible=True)
    ao_financier = fields.Many2one('ao.ao', "AO", invisible=True)
    ao_clause_particuliere = fields.Many2one('ao.ao', "AO", invisible=True)
    dossier_add_id = fields.Many2one('ao.ao', "AO", invisible=True)
    ao_cps_signe = fields.Many2one('ao.ao', "AO", invisible=True)
    ao_autre_dossier = fields.Many2one('ao.ao', "AO", invisible=True)
    state = fields.Selection([('draft', 'Nouveau'), ('progres', 'En cours'), ('done', u'terminé'),
                               ('close', u'Clôturer')],
                             default='draft', string="Etat", track_visibility='onchange')
    comments = fields.Text('Remarques', track_visibility='onchange')
    copie = fields.Integer('Nombre de copies', compute='_compute_details', store=True)
    original = fields.Integer("Nombre d'originaux", compute='_compute_details', store=True)
    date_realisation = fields.Date('Date de réalisation', track_visibility='onchange')
    traitement_ids = fields.One2many('dossier.traitement', 'dossier_id', 'Etape de traitement', track_visibility='onchange')


    def action_draft(self):
        self.write({'state': 'draft'})
        return True


    def action_done(self):
        if any(not x.attachment_ids for x in self):
            raise ValidationError('Vous ne pouvez pas terminer un dossier sans joindre un fichier à celui-ci!')
        self.write({'state': 'done'})
        checklist_id = self.env['ao.checklist'].search([('dossier_line', 'in', self.mapped('id'))])
        checklist_id.write({'date_realisation': fields.Date.context_today(self)})
        template_id = self.env.ref("ao.email_template_dossier_done")

        for rec in self:
            # message_follower_ids =  ${str.join(', ', object.intervenant_ids.mapped('name'))}
            ao_id = rec.ao_tech or rec.dossier_tech or rec.ao_dossier_admin or rec.ao_financier or rec.ao_clause_particuliere or rec.dossier_add_id or rec.ao_cps_signe or rec.ao_autre_dossier

            rec.message_subscribe([x.partner_id.id for x in ao_id.message_follower_ids])

            rec.message_post_with_template(template_id=template_id.id,)
                                           # message_type='email')
        return True


    def action_progres(self):
        self.write({'state': 'progres'})
        return True


    def action_close(self):
        self.write({'state': 'close'})
        return True


    @api.depends('name','ao_tech','dossier_tech','ao_financier', 'ao_clause_particuliere','dossier_add_id', 'ao_autre_dossier')
    def get_complete_name(self):
        for rec in self:
            if rec.name:
                name = ""
                if rec.ao_tech:
                    name = "Offre technique: "
                elif rec.dossier_tech:
                    name = "Dossier technique: "
                elif rec.ao_financier:
                    name = "Offre financière: "
                elif rec.ao_clause_particuliere:
                    name = "Clause particulière: "
                elif rec.ao_dossier_admin:
                    name = "Dossier Administratif: "
                elif rec.ao_cps_signe:
                    name = "CPS signé: "
                elif rec.dossier_add_id:
                    name = "Dossier additif: "
                elif rec.ao_autre_dossier:
                    name = "Autres: "

                rec.complete_name = name + rec.name


    @api.depends('ao_tech', 'dossier_tech', 'ao_dossier_admin', 'dossier_add_id', 'ao_autre_dossier',
                 'ao_financier', 'ao_clause_particuliere', 'ao_cps_signe',
                 'ao_tech.dossier_detail_ids', 'dossier_tech.dossier_detail_ids', 'ao_dossier_admin.dossier_detail_ids', 'dossier_add_id.dossier_detail_ids',
                 'ao_financier.dossier_detail_ids', 'ao_clause_particuliere.dossier_detail_ids', 'ao_cps_signe.dossier_detail_ids', 'ao_autre_dossier.dossier_detail_ids',
                 'ao_tech.dossier_detail_ids.copie', 'dossier_tech.dossier_detail_ids.copie', 'ao_dossier_admin.dossier_detail_ids.copie', 'dossier_add_id.dossier_detail_ids.copie',
                 'ao_financier.dossier_detail_ids.copie', 'ao_clause_particuliere.dossier_detail_ids.copie', 'ao_cps_signe.dossier_detail_ids.copie', 'ao_autre_dossier.dossier_detail_ids.copie',
                 'ao_tech.dossier_detail_ids.original', 'dossier_tech.dossier_detail_ids.original', 'ao_dossier_admin.dossier_detail_ids.original', 'ao_autre_dossier.dossier_detail_ids.original',
                 'ao_financier.dossier_detail_ids.original', 'ao_clause_particuliere.dossier_detail_ids.original', 'ao_cps_signe.dossier_detail_ids.original', 'dossier_add_id.dossier_detail_ids.original'

                 )
    def _compute_details(self):
        detail_obj = self.env['ao.dossier.detail']
        for rec in self:
            if rec.ao_tech:
                detail_id = detail_obj.search([('dossier', '=', 'offre_tech')], limit=1)
                if detail_id:
                    rec.copie = detail_id.copie
                    rec.original = detail_id.original
            if rec.dossier_tech:
                detail_id = detail_obj.search([('dossier', '=', 'dossier_tech')], limit=1)
                if detail_id:
                    rec.copie = detail_id.copie
                    rec.original = detail_id.original
            if rec.ao_dossier_admin:
                detail_id = detail_obj.search([('dossier', '=', 'dossier_admin')], limit=1)
                if detail_id:
                    rec.copie = detail_id.copie
                    rec.original = detail_id.original
            if rec.ao_financier:
                detail_id = detail_obj.search([('dossier', '=', 'offre_financiere')], limit=1)
                if detail_id:
                    rec.copie = detail_id.copie
                    rec.original = detail_id.original
            if rec.ao_clause_particuliere:
                detail_id = detail_obj.search([('dossier', '=', 'clause_particuliere')], limit=1)
                if detail_id:
                    rec.copie = detail_id.copie
                    rec.original = detail_id.original
            if rec.dossier_add_id:
                detail_id = detail_obj.search([('dossier', '=', 'dossier_additif')], limit=1)
                if detail_id:
                    rec.copie = detail_id.copie
                    rec.original = detail_id.original

            if rec.ao_cps_signe:
                detail_id = detail_obj.search([('dossier', '=', 'cps_signe')], limit=1)
                if detail_id:
                    rec.copie = detail_id.copie
                    rec.original = detail_id.original
            if rec.ao_autre_dossier:
                detail_id = detail_obj.search([('dossier', '=', 'autre')], limit=1)
                if detail_id:
                    rec.copie = detail_id.copie
                    rec.original = detail_id.original



class AoDossierdetail(models.Model):
    _name = 'ao.dossier.detail'

    dossier = fields.Selection([('dossier_tech', 'Dossier technique'),
                              ('dossier_admin', 'Dossier administratif'),
                              ('dossier_additif', u'Dossier additif'),
                              ('cps_signe', u'CPS signé'),
                              ('offre_tech', 'Offre technique'),
                              ('offre_financiere', u'Offre financière'),
                              ('clause_particuliere', u'Clause particulière'),
                              ('autre', u'Autres'),
                              ],
                             string=u"Dossier", required=True)
    copie = fields.Integer('Nombre de copies', required=True)
    original = fields.Integer("Nombre d'originaux")
    ao_id = fields.Many2one('ao.ao', "Appel d'offre")


class DossierTypeDocument(models.Model):
    _name = 'dossier.type.document'

    name = fields.Char('Nom')
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


class DossierTraitement(models.Model):
    _name = 'dossier.traitement'

    date = fields.Date('Date', default=fields.Date.context_today)
    date_realisation = fields.Date('Date réalisation')
    name = fields.Char('Description')
    user_id = fields.Many2one('res.partner', 'Responsable', required=True)
    etat = fields.Selection([('nouveau', 'Nouveau'), ('encours', 'Encours'), ('done', 'Terminé')])
    dossier_id = fields.Many2one('ao.dossier', 'Dossier')

    @api.onchange('etat')
    def onchange_etat(self):
        if self.etat == 'done':
            self.date_realisation = fields.Date.context_today(self)

