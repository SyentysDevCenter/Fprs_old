from odoo import api, fields, models

class Ao(models.Model):
    _inherit = 'ao.ao'

    responsable = fields.Many2one('res.partner', default=lambda r: r.env.user.partner_id.id,
                                  track_visibility='onchange', string="Chargé d'affaire")
    objet = fields.Text(track_visibility='onchange', string='Opération')
    adresse_operation = fields.Text("Adresse de l'opération")
    estimation_mo = fields.Float("Montant HT", track_visibility='onchange')
    estimation_ttc = fields.Float(u'Montant TTC', compute='_compute_totat_ttc', inverse='_set_estimation_ttc', store=True)
    financement = fields.Text('Détail Montant HT',  track_visibility='onchange')
    validity = fields.Integer("Validité de l'offre (jr)")
    copropriete = fields.Boolean('Coproprieté')
    date_remise_ca = fields.Date('Remise au CA')
    state = fields.Selection(selection_add=[('non_repondu', 'Non répondu')],ondelete={'non_repondu': 'cascade'})
    remise_plis = fields.Text('Remise des plis')
    ao_gardien_ids = fields.One2many('ao.gardien', 'ao_id', 'Gardiens')
    mo_delegue_id = fields.Many2one('res.partner', "Maitrise d'oeuvre BET",  track_visibility='onchange')
    jugement_offre_ids = fields.One2many('ao.jugement.offre', 'ao_id', 'Jugement des offre')
    rapport_amiante = fields.Boolean('Rapport amiante fourni')
    presence_amiante = fields.Boolean('Présence amiante')
    Localisation_amiante = fields.Boolean("Localisation d'amiante")
    negociation_ids = fields.One2many('ao.negociation', 'ao_id', 'Négociation')


    def button_non_repondu(self):
        self.write({'state': 'non_repondu'})



class AoGardien(models.Model):
    _name = 'ao.gardien'

    name = fields.Char('Nom')
    phone = fields.Char('Téléphone')
    note = fields.Char('Note')
    ao_id = fields.Many2one('ao.ao')


class AoNegociation(models.Model):
    _name = 'ao.negociation'

    ao_id = fields.Many2one('ao.ao')
    name = fields.Text('Décision')
    contact_id = fields.Many2one('res.partner', 'Contact')
    date_contact = fields.Datetime('Date du contact')
    date_reponse = fields.Datetime('Date réponse')


class AoJugementOffre(models.Model):
    _name = 'ao.jugement.offre'

    name = fields.Char('Critère')
    note = fields.Float('Note')
    commentaire = fields.Char('Commentaire')
    ao_id = fields.Many2one('ao.ao')



