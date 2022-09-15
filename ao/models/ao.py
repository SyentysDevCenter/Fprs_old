# -*- coding: utf-8 -*-

from odoo import api, fields, models
import datetime
from odoo.exceptions import ValidationError


class Ao(models.Model):
    _name = "ao.ao"
    _inherit = ['mail.thread', 'portal.mixin', 'mail.activity.mixin']
    _description = "Appel d'offre"


    @api.depends('attributaire_id', 'concurent_line')
    def _compute_montant_attribution(self):
        for rec in self:
            for line in rec.concurent_line:
                if line.concurrent == rec.attributaire_id:
                    rec.montant_attribution = line.montant
                    break




    def name_get(self):
        result = []
        for record in self:
            if record.name and record.lot:
                result.append((record.id, record.name + '/ Lot N° ' + record.lot))
            if record.name and not record.lot:
                result.append((record.id, record.name))
        return result



    name = fields.Char(u"Numéro", required=True, track_visibility='always')
    appellation = fields.Char(string="Appellation courante", track_visibility='onchange')
    date_creation = fields.Date(u"Date création",
                                required=True,
                                default=fields.Date.context_today)
    date_recup_cps = fields.Date(u"Date récup CPS", track_visibility='onchange')
    objet = fields.Text(track_visibility='onchange')
    name_ao = fields.Char(u"Appel d'offre N°", required=True, track_visibility='onchange')
    lot = fields.Char('Lot', track_visibility='onchange')

    type = fields.Selection([('o', 'Ouvert'),
                             ('r', 'Restreint'),
                             ('gre', 'Gré à Gré'),
                             ('interet', u"Appel à manifestation d'interêt"),
                             ('consultation', 'Consultation')],
                            default='o', track_visibility='onchange')
    ville = fields.Many2one("ao.ville", track_visibility='onchange')
    country_id = fields.Many2one('res.country', 'Pays', default=lambda self: self.env.ref('base.ma'), track_visibility='onchange')
    estimation_mo = fields.Float("Budget HT", track_visibility='onchange')
    # currency_id = fields.Many2one('res.currency', string='Devise',
    #                               default=lambda self: self.env.user.company_id.currency_id.id)
    taxes = fields.Float(string='Taxes', track_visibility='onchange', default=20)
    estimation_ttc = fields.Float(u'Budget TTC', compute='_compute_totat_ttc', inverse='_set_estimation_ttc', store=True)
    delai_exec = fields.Integer(u"Délai contractuel (en mois)", track_visibility='onchange')
    date_limite = fields.Datetime("Date limite remise AO", track_visibility='onchange')
    lieu_remise = fields.Char(u"Lieu de remise de l'offre", track_visibility='onchange')
    # organisme_ids = fields.Many2many("ao.organisme",
    #                                   "ao_organisme_rel",
    #                                   "ao_id",
    #                                   "organisme_id",
    #                                   string="Organismes", track_visibility='onchange')
    payment_term = fields.Many2one('account.payment.term', 'Conditions de paiement', track_visibility='onchange')
    date_dg = fields.Date(u"Date décision DG", track_visibility='onchange')
    date_depo_ao = fields.Date(u"Date remise de l'offre",  track_visibility='onchange')
    visite_ids = fields.One2many('visite.lieu', 'ao_id', "Visite des lieux", copy=True,  track_visibility='onchange')
    checklist_lines = fields.One2many('ao.checklist', 'ao_id', "Checklist", copy=True, track_visibility='onchange')
   # Dossier
    offre_technique_ligne = fields.One2many('ao.dossier', 'ao_tech', u"Offre technique", copy=True,  track_visibility='onchange')
    dossier_technique_admin = fields.One2many('ao.dossier',
                                              'dossier_tech',
                                              u"Dossier technique", copy=True,  track_visibility='onchange')
    offre_financiere = fields.One2many('ao.dossier',
                                       'ao_financier',
                                       u"Offre financière", copy=True,  track_visibility='onchange')
    clause_particuliere = fields.One2many('ao.dossier',
                                          'ao_clause_particuliere',
                                          u"Clauses particulières", copy=True,  track_visibility='onchange')
    dossier_additif_ids = fields.One2many('ao.dossier',
                                          'dossier_add_id',
                                          u"Dossier additifs", copy=True,  track_visibility='onchange')

    cps_signe_ids = fields.One2many('ao.dossier',
                                    'ao_cps_signe',
                                    u"CPS signé", copy=True,  track_visibility='onchange')

    dossier_admin_ids = fields.One2many('ao.dossier',
                                    'ao_dossier_admin',
                                    u"DOssier administratifs", copy=True,  track_visibility='onchange')
    autre_dossier_ids = fields.One2many('ao.dossier',
                                    'ao_autre_dossier',
                                    u"Autres", copy=True,  track_visibility='onchange')

    dossier_detail_ids = fields.One2many('ao.dossier.detail', 'ao_id', 'Détail des dossier', copy=True,  track_visibility='onchange')
    offre_technique_count = fields.Integer(compute="get_offre_technique_count", string=u"# Offre technique", store=True)
    dossier_technique_count = fields.Integer(compute="get_dossier_technique_count", string=u"# Dossier technique",
                                             store=True)
    offre_financiere_count = fields.Integer(compute="get_offre_financiere_count", string=u"# Offre financière",
                                            store=True)
    clause_particuliere_count = fields.Integer(compute="get_clause_particuliere_count", string=u"# Clause particulière",
                                               store=True)
    dossier_additif_count = fields.Integer(compute="get_dossier_additif_count", string=u"# Dossier additif",
                                               store=True)

    cps_signe_count = fields.Integer(compute="get_cps_signe_count", string=u"# CPS signé", store=True)
    dossier_admin_count = fields.Integer(compute="get_dossier_admin_count", string=u"# Dossier administratif",
                                         store=True)
    autre_dossier_count = fields.Integer(compute="get_autre_dossier_count", string=u"# Autres",
                                         store=True)


    risk_ids = fields.One2many('ao.risk', 'ao_id', 'Risques',  track_visibility='onchange')
    date_retrait = fields.Date("Date retrait",  track_visibility='onchange')
    mode_retrait = fields.Selection([('e', u'Espéce'),
                                     ('c', u'Chèque'),
                                     ('gratuit', 'Gratuit')],
                                    "Mode retrait",  track_visibility='onchange')
    ref_paiement = fields.Char(u"Référence paiement",  track_visibility='onchange')
    # --- Caution
    caution_ids = fields.One2many('bank.caution.line', 'ao_id', 'Cautions',  track_visibility='onchange')
    caution_prov = fields.Float("Caution provisoire",  track_visibility='onchange')
    date_caution = fields.Date(u"Date dépôt caution",  track_visibility='onchange')
    banque = fields.Many2one('res.bank', "Banque",  track_visibility='onchange')
    compte = fields.Many2one('res.partner.bank', string=u'N° du compte',  track_visibility='onchange')
    # date_retrait_caution = fields.Date("Date retrait",  track_visibility='onchange')
    # date_restitution = fields.Date(u"Date restitution",  track_visibility='onchange')
    # etat_caution = fields.Selection([('o', 'Ouverte'),
    #                                  ('r', u'Récupérée'),
    #                                  ('perdu', 'Perdue')],
    #                                 u"Etat caution",  track_visibility='onchange')
    # motif_restitution_caution = fields.Char('Motif de restitution',  track_visibility='onchange')
    # ----
    # source_financement = fields.Char('Source de financement',  track_visibility='onchange')
    condition_facturation = fields.Text('Condition de facturation',  track_visibility='onchange')
    date_relance = fields.Date(u"Date relance",  track_visibility='onchange')
    note = fields.Text( track_visibility='onchange')
    montant_soumission = fields.Float("Budget",  track_visibility='onchange')
    classement = fields.Integer("Classement", compute='_compute_classement', store=True)
    date_jugement = fields.Date("Date jugement",  track_visibility='onchange')
    attributaire_id = fields.Many2one('ao.concurent', "Attributaire",  track_visibility='onchange' )
    montant_attribution = fields.Float(compute="_compute_montant_attribution", store=True,
                                       string="Montant attribution")
    concurent_line = fields.One2many('ao.jugement.line', 'ao_id', copy=True,  track_visibility='onchange')
    # reglement_line = fields.One2many('ao.reglement', 'ao_id', u"Règlement AO", copy=True,  track_visibility='onchange')
    livrable_line = fields.One2many('ao.livrable.demande', 'ao_id', string=u"Livrables demandés", copy=True,  track_visibility='onchange')

    jugement_administratif_line = fields.One2many('ao.jugement.administratif',
                                                  'ao_id',
                                                  string=u"Jugement administratif", copy=True,  track_visibility='onchange')
    valide_administratif = fields.Boolean(default=False, copy=False,  track_visibility='onchange')
    jugement_technique_line = fields.One2many('ao.jugement.technique',
                                              'ao_id',
                                              string=u"Jugement technique", copy=True,  track_visibility='onchange')
    valide_technique = fields.Boolean(default=False, copy=False,  track_visibility='onchange')
    motif_rejet_id = fields.Many2one('ao.motif.rejet', string=u"Motif de rejet",  track_visibility='onchange')
    responsable = fields.Many2one('res.partner', default=lambda r: r.env.user.partner_id.id, track_visibility='onchange')
    motif_annulation_soumission = fields.Char(u"Motif d'annulation de la soumission:",  track_visibility='onchange')
    os = fields.Char(string="OS",  track_visibility='onchange')
    date_demarrage = fields.Datetime(u'Date estimée de démarrage',  track_visibility='onchange')
    commentaires = fields.Text('Commentaires',  track_visibility='onchange')
    type_prestation = fields.Many2one('ao.prestation', u"Type de Prestations ",  track_visibility='onchange')
    note_technique = fields.Integer('Note technique (NT)',  track_visibility='onchange')
    note_global = fields.Integer('Note globale (NG)',  track_visibility='onchange')
    note_fianciere = fields.Integer('Note financiere (NF)',  track_visibility='onchange')
    jugement_final = fields.Text('Jugement final',  track_visibility='onchange')
    financement = fields.Text('Financement',  track_visibility='onchange')
    fiscal_position_id = fields.Many2one('account.fiscal.position', 'Position fiscal',  track_visibility='onchange')
    # type_ao = fields.Selection([('national', 'National'),('international', 'International')], default='national', string='National/International',  track_visibility='onchange')
    # preference_international = fields.Boolean('Préférence international',  track_visibility='onchange')
    # taux = fields.Float('Taux',  track_visibility='onchange')

    agreement_ids = fields.Many2many('ao.agreement', 'ao_agreement_rel', 'ao_id', 'agreement_id', "Agréments",  track_visibility='onchange')
    cps_change_ids = fields.One2many('ao.cps.change', 'ao_id', 'Changement du CPS', copy=True,  track_visibility='onchange')
    # partners
    intervenant_partner_ids = fields.Many2many('res.partner', 'ao_intervenant_rel', 'ao_id', 'partner_id', "Intervenants",  track_visibility='onchange')
    partner_id = fields.Many2one('res.partner', "Client",  track_visibility='onchange')
    resp_remise = fields.Many2one('res.users', "Offre remise par",  track_visibility='onchange')
    mo_id = fields.Many2one('res.partner', "Maitre d'ouvrage",  track_visibility='onchange')
    mo_delegue_id = fields.Many2one('res.partner', "Maitre d'ouvrage délégué",  track_visibility='onchange')
    bailleur_id = fields.Many2one('res.partner', "Bailleur",  track_visibility='onchange')
    contact_ids = fields.Many2many('res.partner', 'ao_contacts_rel', 'ao_id','partner_id', string='Contacts', domain=[('active', '=', True)],  track_visibility='onchange')  # force "active_test" domain to bypass _search() override

    # Statistique dossier
    dossier_admin_realise = fields.Integer(u'Réalisé', compute='get_dossier_stat', store=True)
    dossier_admin_realise_percent = fields.Float(u'%', compute='get_dossier_stat', store=True)
    dossier_techn_realise = fields.Integer(u'Réalisé', compute='get_dossier_stat', store=True)
    dossier_techn_realise_percent = fields.Float(u'Réalisé (%)', compute='get_dossier_stat', store=True)
    dossier_add_realise = fields.Integer(u'Réalisé', compute='get_dossier_stat', store=True)
    dossier_add_realise_percent = fields.Float(u'Réalisé (%)', compute='get_dossier_stat', store=True)
    clause_particuliere_realise = fields.Integer(u'Réalisé', compute='get_dossier_stat', store=True)
    clause_particuliere_realise_percent = fields.Float(u'Réalisé (%)', compute='get_dossier_stat', store=True)
    cps_signe_realise = fields.Integer(u'Réalisé', compute='get_dossier_stat', store=True)
    cps_signe_realise_percent = fields.Float(u'Réalisé (%)', compute='get_dossier_stat', store=True)
    offre_techn_realise = fields.Integer(u'Réalisé', compute='get_dossier_stat', store=True)
    offre_techn_realise_percent = fields.Float(u'%', compute='get_dossier_stat', store=True)
    offre_finance_realise = fields.Integer(u'Réalisé', compute='get_dossier_stat', store=True)
    offre_finance_realise_percent = fields.Float(u'Réalisé (%)', compute='get_dossier_stat', store=True)
    autre_dossier_realise = fields.Integer(u'Réalisé', compute='get_dossier_stat', store=True)
    autre_dossier_realise_percent = fields.Float(u'Réalisé (%)', compute='get_dossier_stat', store=True)
    global_realise = fields.Integer(compute='compute_global', string=u"Réalisé", store=True)
    dossier_global = fields.Integer(compute='compute_global', string=u"Nombre de dossier", store=True)
    global_realise_percent = fields.Integer(compute='compute_global', string=u"Réalisé(%)", store=True)

    dossier_admin_cloture = fields.Integer(u'Clôturé', compute='get_dossier_stat', store=True)
    dossier_admin_cloture_percent = fields.Float(u'%', compute='get_dossier_stat', store=True)
    dossier_techn_cloture = fields.Integer(u'Clôturé', compute='get_dossier_stat', store=True)
    dossier_techn_cloture_percent = fields.Float(u'Clôturé (%)', compute='get_dossier_stat', store=True)
    dossier_add_cloture = fields.Integer(u'Clôturé', compute='get_dossier_stat', store=True)
    dossier_add_cloture_percent = fields.Float(u'Clôturé (%)', compute='get_dossier_stat', store=True)
    clause_particuliere_cloture = fields.Integer(u'Clôturé', compute='get_dossier_stat', store=True)
    clause_particuliere_cloture_percent = fields.Float(u'Clôturé (%)', compute='get_dossier_stat', store=True)
    cps_signe_cloture = fields.Integer(u'Clôturé', compute='get_dossier_stat', store=True)
    cps_signe_cloture_percent = fields.Float(u'Clôturé (%)', compute='get_dossier_stat', store=True)
    offre_techn_cloture = fields.Integer(u'Clôturé', compute='get_dossier_stat', store=True)
    offre_techn_cloture_percent = fields.Float(u'%', compute='get_dossier_stat', store=True)
    offre_finance_cloture = fields.Integer(u'Clôturé', compute='get_dossier_stat', store=True)
    offre_finance_cloture_percent = fields.Float(u'Clôturé (%)', compute='get_dossier_stat', store=True)
    autre_dossier_cloture = fields.Integer(u'Clôturé', compute='get_dossier_stat', store=True)
    autre_dossier_cloture_percent = fields.Float(u'Clôturé (%)', compute='get_dossier_stat', store=True)
    global_cloture = fields.Integer(compute='compute_global', string=u"Clôturé", store=True)
    global_cloture_percent = fields.Integer(compute='compute_global', string=u"Clôturé(%)", store=True)


    motif_refus = fields.Text('Motif de refus')
    date_refus = fields.Date('Date de refus')

    admission_ids = fields.One2many('ao.admission', 'ao_id', u"Critères d'admissibilité")
    evaluation_ids = fields.One2many('ao.evaluation', 'ao_id', u"Critères d'évaluation")
    critere_elimination = fields.Text("Critères d'élimination")
    admission_file = fields.Binary("Admissibilité")
    evaluation_file = fields.Binary("Evaluation")
    risque_file = fields.Binary("Risque")
    cps_file = fields.Binary("CPS")

    elimination_file = fields.Binary("Elimination")
    state = fields.Selection([('new', 'Nouveau'),
                              # ('envoye', u'Envoyé DG'),
                              ('valideDG', u'Prévalidation'),
                              ('valideFinal', 'Validation finale'),
                              ('traitement', 'En traitement'),
                              ('valideSoumis', 'Validation soumission'),
                              ('refus', u'Refusé'),
                              ('depose', u'Déposé'),
                              ('gagne', u'Gagné'),
                              ('perdu', 'Perdu'),
                              ('soumissionAnnule', u'Soumission annulée')],
                             default='new', required=True,  track_visibility='onchange')


    @api.depends('estimation_mo', 'taxes')
    def _compute_totat_ttc(self):
        for rec in self:
            # res = rec.tax_ids.compute_all(rec.estimation_mo, currency=None, quantity=1.0, product=None, partner=None)
            rec.estimation_ttc = rec.estimation_mo * (1+rec.taxes/100)

    def _set_estimation_ttc(self):
        # res = self.tax_ids.compute_all(self.estimation_mo, currency=None, quantity=1.0, product=None, partner=None)

        self.estimation_mo = self.estimation_ttc / (1+self.taxes/100)




    @api.depends('offre_technique_count', 'dossier_technique_count', 'offre_financiere_count',
                 'clause_particuliere_count', 'cps_signe_count', 'dossier_admin_count', 'dossier_additif_count', 'autre_dossier_count',
                 'dossier_admin_realise', 'dossier_techn_realise', 'dossier_add_realise', 'autre_dossier_realise',
                 'cps_signe_realise', 'offre_techn_realise', 'offre_finance_realise', 'clause_particuliere_realise',
                 'dossier_admin_cloture', 'dossier_techn_cloture', 'dossier_add_cloture', 'clause_particuliere_cloture',
                 'cps_signe_cloture', 'offre_techn_cloture', 'offre_finance_cloture', 'autre_dossier_cloture'
                 )
    def compute_global(self):
        for rec in self:
            rec.dossier_global = rec.offre_technique_count + rec.dossier_additif_count + rec.dossier_technique_count + rec.offre_financiere_count + rec.clause_particuliere_count + rec.cps_signe_count + rec.dossier_admin_count + rec.autre_dossier_count

            rec.global_realise = (rec.dossier_admin_realise + rec.dossier_techn_realise + rec.dossier_add_realise + rec.clause_particuliere_realise + rec.cps_signe_realise + rec.offre_techn_realise + rec.offre_finance_realise + rec.autre_dossier_realise)
            rec.global_cloture = (rec.dossier_admin_cloture + rec.dossier_techn_cloture + rec.dossier_add_cloture + rec.clause_particuliere_cloture + rec.cps_signe_cloture + rec.offre_techn_cloture + rec.offre_finance_cloture + rec.autre_dossier_cloture)
            if rec.dossier_global:
                rec.global_realise_percent = (rec.global_realise/rec.dossier_global)*100
                rec.global_cloture_percent = (rec.global_cloture/rec.dossier_global)*100


    def confirm_all_checklist(self):
        for rec in self:
            for line in rec.checklist_lines.filtered(lambda r: not r.dossier_line):
                line.button_confirme()


    @api.depends('offre_technique_ligne', 'offre_technique_ligne.state',
                 'dossier_technique_admin', 'dossier_technique_admin.state',
                 'offre_financiere', 'offre_financiere.state',
                 'clause_particuliere', 'clause_particuliere.state',
                 'cps_signe_ids', 'cps_signe_ids.state',
                 'dossier_admin_ids', 'dossier_admin_ids.state',
                 'dossier_additif_ids', 'dossier_additif_ids.state',
                 'autre_dossier_ids', 'autre_dossier_ids.state',
                 )
    def get_dossier_stat(self):
        for rec in self:
            if len(rec.offre_technique_ligne) != 0:
                realise = len(rec.offre_technique_ligne.filtered(lambda r: r.state == 'done'))
                cloture = len(rec.offre_technique_ligne.filtered(lambda r: r.state == 'close'))
                rec.offre_techn_realise = realise
                rec.offre_techn_realise_percent = realise / len(rec.offre_technique_ligne) * 100
                rec.offre_techn_cloture = cloture
                rec.offre_techn_cloture_percent = cloture / len(rec.offre_technique_ligne) * 100

            if len(rec.dossier_technique_admin) != 0:
                realise = len(rec.dossier_technique_admin.filtered(lambda r: r.state == 'done'))
                cloture = len(rec.dossier_technique_admin.filtered(lambda r: r.state == 'close'))
                rec.dossier_techn_realise = realise
                rec.dossier_techn_realise_percent = realise / len(rec.dossier_technique_admin) * 100
                rec.dossier_techn_cloture = cloture
                rec.dossier_techn_cloture_percent = cloture / len(rec.dossier_technique_admin) * 100

            if len(rec.offre_financiere) != 0:
                realise = len(rec.offre_financiere.filtered(lambda r: r.state == 'done'))
                cloture = len(rec.offre_financiere.filtered(lambda r: r.state == 'close'))
                rec.offre_finance_realise = realise
                rec.offre_finance_realise_percent = realise / len(rec.offre_financiere) * 100
                rec.offre_finance_cloture = cloture
                rec.offre_finance_cloture_percent = cloture / len(rec.offre_financiere) * 100

            if len(rec.dossier_additif_ids) != 0:
                realise = len(rec.dossier_additif_ids.filtered(lambda r: r.state == 'done'))
                cloture = len(rec.dossier_additif_ids.filtered(lambda r: r.state == 'close'))
                rec.dossier_add_realise = realise
                rec.dossier_add_realise_percent = realise / len(rec.dossier_additif_ids) * 100
                rec.dossier_add_cloture = cloture
                rec.dossier_add_cloture_percent = cloture / len(rec.dossier_additif_ids) * 100

            if len(rec.clause_particuliere) != 0:
                realise = len(rec.clause_particuliere.filtered(lambda r: r.state == 'done'))
                cloture = len(rec.clause_particuliere.filtered(lambda r: r.state == 'close'))
                rec.clause_particuliere_realise = realise
                rec.clause_particuliere_realise_percent = realise / len(rec.clause_particuliere) * 100
                rec.clause_particuliere_cloture = cloture
                rec.clause_particuliere_cloture_percent = cloture / len(rec.clause_particuliere) * 100

            if len(rec.cps_signe_ids) != 0:
                realise = len(rec.cps_signe_ids.filtered(lambda r: r.state == 'done'))
                cloture = len(rec.cps_signe_ids.filtered(lambda r: r.state == 'close'))
                rec.cps_signe_realise = realise
                rec.cps_signe_realise_percent = realise / len(rec.cps_signe_ids) * 100
                rec.cps_signe_cloture = cloture
                rec.cps_signe_cloture_percent = cloture / len(rec.cps_signe_ids) * 100

            if len(rec.dossier_admin_ids) != 0:
                realise = len(rec.dossier_admin_ids.filtered(lambda r: r.state == 'done'))
                cloture = len(rec.dossier_admin_ids.filtered(lambda r: r.state == 'close'))
                rec.dossier_admin_realise = realise
                rec.dossier_admin_realise_percent = realise / len(rec.dossier_admin_ids) * 100
                rec.dossier_admin_cloture = cloture
                rec.dossier_admin_cloture_percent = cloture / len(rec.dossier_admin_ids) * 100

            if len(rec.autre_dossier_ids) != 0:
                realise = len(rec.autre_dossier_ids.filtered(lambda r: r.state == 'done'))
                cloture = len(rec.autre_dossier_ids.filtered(lambda r: r.state == 'close'))
                rec.autre_dossier_realise = realise
                rec.autre_dossier_realise_percent = realise / len(rec.autre_dossier_ids) * 100
                rec.autre_dossier_cloture = cloture
                rec.autre_dossier_cloture_percent = cloture / len(rec.autre_dossier_ids) * 100

        return True


    @api.depends('offre_technique_ligne')
    def get_offre_technique_count(self):
        for rec in self:
            rec.offre_technique_count = len(rec.offre_technique_ligne)


    @api.depends('cps_signe_ids')
    def get_cps_signe_count(self):
        for rec in self:
            rec.cps_signe_count = len(rec.cps_signe_ids)


    @api.depends('autre_dossier_ids')
    def get_autre_dossier_count(self):
        for rec in self:
            rec.autre_dossier_count = len(rec.autre_dossier_ids)

    @api.depends('dossier_technique_admin')
    def get_dossier_technique_count(self):
        for rec in self:
            rec.dossier_technique_count = len(rec.dossier_technique_admin)

    @api.depends('dossier_admin_ids')
    def get_dossier_admin_count(self):
        for rec in self:
            rec.dossier_admin_count = len(rec.dossier_admin_ids)

    @api.depends('offre_financiere')
    def get_offre_financiere_count(self):
        for rec in self:
            rec.offre_financiere_count = len(rec.offre_financiere)

    @api.depends('clause_particuliere')
    def get_clause_particuliere_count(self):
        for rec in self:
            rec.clause_particuliere_count = len(rec.clause_particuliere)

    @api.depends('dossier_additif_ids')
    def get_dossier_additif_count(self):
        for rec in self:
            rec.dossier_additif_count = len(rec.dossier_additif_ids)

    @api.depends('montant_soumission', 'concurent_line')
    def _compute_classement(self):
        for rec in self:
            if rec.concurent_line:
                concurents_list = rec.concurent_line.filtered(lambda r: r.ecarte is False)
                concurents = [(x, x.montant) for x in concurents_list]
                concurents.append((rec, rec.montant_soumission))
                concurents.sort(key=lambda r: r[1])
                rec.classement = concurents.index((rec, rec.montant_soumission)) + 1
                for line in concurents_list:
                    line.write({'classement': concurents.index((line, line.montant)) + 1})

    def get_offre_technique(self):
        self.ensure_one()
        return {
            'name': 'Offres techniques',
            'type': 'ir.actions.act_window',
            'res_model': 'ao.dossier',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [("ao_tech", "=", self.id)],
            'context': {'default_ao_tech': self.id, 'ao_tech':self.id},
            'target': 'current',
            }

    def get_autre_dossiers(self):
        self.ensure_one()
        return {
            'name': 'Autres',
            'type': 'ir.actions.act_window',
            'res_model': 'ao.dossier',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [("ao_autre_dossier", "=", self.id)],
            'context': {'default_ao_autre_dossier': self.id, 'ao_autre_dossier':self.id},
            'target': 'current',
            }


    def get_dossier_admin(self):
        self.ensure_one()
        return {
            'name': 'Dossiers administartifs',
            'type': 'ir.actions.act_window',
            'res_model': 'ao.dossier',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [("ao_dossier_admin", "=", self.id)],
            'context': {'default_ao_dossier_admin': self.id, 'ao_dossier_admin':self.id},
            'target': 'current',
        }

    def get_cps_signe(self):
        self.ensure_one()
        return {
            'name': 'Cps cignés',
            'type': 'ir.actions.act_window',
            'res_model': 'ao.dossier',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [("ao_cps_signe", "=", self.id)],
            'context': {'default_ao_cps_signe': self.id, 'ao_cps_signe': self.id},
            'target': 'current',
        }

    def get_dossier_technique(self):
        self.ensure_one()
        dossier_technique_lines = [dossier_technique.id for dossier_technique in self.dossier_technique_admin]
        return {
            'name': 'Dossiers techniques',
            'type': 'ir.actions.act_window',
            'res_model': 'ao.dossier',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [("dossier_tech", "=", self.id)],
            'context': {'default_dossier_tech': self.id, 'dossier_tech': self.id},
            'target': 'current',
        }



    def get_offre_financiere(self):
        self.ensure_one()
        return {
            'name': 'Offres financières',
            'type': 'ir.actions.act_window',
            'res_model': 'ao.dossier',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [("ao_financier", "=", self.id)],
            'context': {'default_ao_financier': self.id, 'ao_financier': self.id},
            'target': 'current',
        }

    def get_clause_particuliere(self):
        self.ensure_one()
        return {
            'name': 'Clauses particulières',
            'type': 'ir.actions.act_window',
            'res_model': 'ao.dossier',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [("ao_clause_particuliere", "=", self.id)],
            'context': {'default_ao_clause_particuliere': self.id, 'ao_clause_particuliere': self.id},
            'target': 'current',
        }

    def get_dossier_additif(self):
        self.ensure_one()
        return {
            'name': 'Dossier additif',
            'type': 'ir.actions.act_window',
            'res_model': 'ao.dossier',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'domain': [("dossier_add_id", "=", self.id)],
            'context': {'default_dossier_add_id': self.id, 'dossier_add_id': self.id},
            'target': 'current',
        }

    def copy(self, default=None):
        for rec in self:
            default = dict(default or {})
            default.update({'name': rec.name + ' (copie)',})
            return super(Ao, rec).copy(default)

    # Boutons Workflow
    def button_confirme(self):
        for rec in self:
            rec.state = 'valideDG'
        return True

    def button_valider(self):
        for rec in self:
            rec.state = 'valideDG'
        return  True

    def button_refuser(self):
        for rec in self:
            rec.state = 'refus'
        return True

    def button_valide_final(self):
        for rec in self:
            rec.write({'state': 'valideFinal'})
        return True

    def button_traitement(self):
        for rec in self:
            rec.write({'state': 'traitement'})
        return True


    def button_annuler_soumission(self):
        for rec in self:
            rec.write({'state': 'soumissionAnnule'})
        return True


    def button_valide_soumission(self):
        for rec in self:
            rec.write({'state': 'valideSoumis'})
        return True


    def button_abandon_soumission(self):
        for rec in self:
            rec.state = 'valideFinal'
        return True


    def button_deposer(self):
        for rec in self:
            rec.write({'state': 'depose'})
        return True


    def button_gagne(self):
        for rec in self:
            rec.write({'state': 'gagne'})
        return True


    def button_perdu(self):
        for rec in self:
            rec.write({'state': 'perdu'})
        return True


    def valider_administratif(self):
        for rec in self:
            rec.valide_administratif = True
        return True


    def valider_technique(self):
        for rec in self:
            rec.valide_technique = True
        return True


