# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.exceptions import ValidationError, UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    display_parent_on_invoice = fields.Boolean(string='Afficher le parent dans les factures')
    use_partner_shipping_id = fields.Boolean(string='Utiliser adresse de livraison')
    texte_facturation = fields.Text(string='Texte de Facturation')
    type_facturation = fields.Selection([
        ('manuelle', 'MANUELLE'),
        ('email','PAR EMAIL'),
        ('chorus', 'CHORUS'),
        ], string='Type de Facturation')

class ResCompany(models.Model):
    _inherit = 'res.company'

    diviseur_total_ht = fields.Float(string='Diviseur Montant HT', required=True, default=1.45)


class AccountMove(models.Model):
    _inherit = 'account.move'

    def button_draft(self):
        if not self.env.user.has_group('account_extend.group_invoice_set_to_draft'):
            raise ValidationError(
                'Vous ne pouvez pas remettre une facture en brouillon !')
        else:
            for move in self:
                lines = move.mapped('line_ids')
                lines_to_cancel = lines.matched_debit_ids + lines.matched_credit_ids
                if lines_to_cancel:
                    lines_to_cancel = lines_to_cancel.mapped('debit_move_id') + lines_to_cancel.mapped('credit_move_id')
                    if any(l.statement_line_id for l in lines_to_cancel):
                        raise ValidationError('Vous ne pouvez pas remettre en brouillant une écriture rapprochée avec un relevé bancaire!')
        res = super().button_draft()
        return res

    def generate_subcontracting_refund(self):
        refund_journal = self.env['account.journal'].search([('type', '=', 'purchase'), ('journal_sous_traitant', '=', True)], limit = 1)
        if not refund_journal:
            raise UserError("Aucun journal d'achat trouvé!")
        if any(l.subcontracting_refund_id for l in self):
            traite = self.filtered(lambda r: r.subcontracting_refund_id)
            raise UserError('Les facture %s sont déjà traitées' % (','.join(traite.mapped('name'))))

        partners = self.mapped('sous_traitant_id')
        refunds = []
        if partners:
            for partner in partners:
                invoices = self.filtered(lambda r: r.sous_traitant_id == partner)
                if sum(l.amount_total_signed for l in invoices) > 0:
                    raise UserError('Le total des avoirs dépasse le total des factures fournisseurs')
                refund_id = self.env['account.move'].create({'partner_id'           : partner.id,
                                                             'move_type'            : 'in_refund',
                                                             'date'                 : fields.Date.context_today(self),
                                                             'invoice_date'         : fields.Date.context_today(self),
                                                             'currency_id'          : self.env.company.currency_id.id,
                                                             'subcontracting_refund': True,
                                                             'invoice_origin'       : ','.join(
                                                                 str(invoices.mapped('name'))),
                                                             'sous_traitant'        : True,
                                                             'soustraitant'         : True,
                                                             'journal_id': refund_journal.id
                                                             })
                refunds.append(refund_id.id)
                lines = invoices.mapped('invoice_line_ids')
                if lines:
                    refund_lines = []

                    for line in lines:
                        subcontract_product_id = refund_id.company_id.subcontract_product_id
                        if not subcontract_product_id:
                            subcontract_product_id = line.product_id and line.product_id
                        line_name = subcontract_product_id.partner_ref or subcontract_product_id.name or line.name
                        price_unit = line.price_unit * (1 - (line.discount / 100.0)) * (
                                    1 + self.env.company.subcontracting_marge / 100)
                        if line.move_id.move_type == 'in_refund':
                            price_unit = (-1) * price_unit
                        refund_lines.append((0, 0, {
                                                    'product_id': subcontract_product_id and subcontract_product_id.id or False,
												   'account_id': subcontract_product_id and subcontract_product_id.property_account_expense_id.id or line.account_id.id or False,
												   'name': line_name,
                                                    'origin_invoice_line_id'  : line.id,
                                                    'quantity'                : line.quantity,
                                                    'price_unit'              : price_unit,
                                                    'product_uom_id'          : line.product_uom_id and line.product_uom_id.id or False,
                                                    'tax_ids'                 : [(6, 0, line.tax_ids.ids)],
                                                    'analytic_account_id'     : line.analytic_account_id and line.analytic_account_id.id,
                                                    'move_id'                 : refund_id.id,
                                                    'exclude_from_invoice_tab': False
                                                    }))
                    refund_id.write({'invoice_line_ids': refund_lines})

                if refund_id:
                    invoices.write({'subcontracting_refund_id': refund_id.id})
        if refunds:
            action = self.sudo().env.ref(
                    "account.action_move_in_refund_type"
            ).read()[0]
            action["domain"] = [('id', 'in', refunds)]
            return action



    def action_open_assistant_sous_traitance(self):
        if not self.env.user.has_group('account_extend.group_assistant_sous_traitance'):
            raise ValidationError("Vous n'êtes pas autorisé à faire cette action!")
        invoice_ids = self.env['account.move'].browse(self._context.get('active_ids', False))
        lines = []
        if invoice_ids:
            for invoice in invoice_ids:
                for line in invoice.invoice_line_ids.filtered(lambda x: x.display_type not in  ('line_section', 'line_note')):
                    vals = (0, 0, {
                        'move_line_id': line.id,
                        'sous_traitance': line.sous_traitance,
                    })
                    lines.append(vals)

            action = self.sudo().env.ref('account_extend.assistant_sous_traitance_wizard_action').read()[0]
            action['views'] = [(self.env.ref('account_extend.assistant_sous_traitance_wizard_view').id, 'form')]
            action['context'] = {'default_line_ids': lines, 'default_active_invoice_line_ids': invoice_ids.invoice_line_ids.ids}
            return action

    @api.constrains('retenue_garantie')
    def _check(self):
        if self.retenue_garantie > 100 or self.retenue_garantie < 0:
            raise ValidationError('Le pourcentage retenue de garantie est une valeur entre 0 et 100 !')
        
    @api.onchange('sale_chantier_id')
    def _onchange_sale_chantier_id(self):
        if self.sale_chantier_id and self.sale_chantier_id.user_id and self.move_type in ('in_invoice', 'in_refund'):
            # get all tags and check if tag exist
            tag_exist = False
            tag_ids = self.env['account.analytic.tag'].search([]).filtered(lambda tag: tag.name.strip().lower() == self.sale_chantier_id.user_id.name.strip().lower())
            if tag_ids:
                tag_exist = tag_ids[0]
            # change tags_to_affect_ids and call apply_tags
            if tag_exist:
                self.tags_to_affect_ids = [(6, 0, [tag_exist.id])]
                self.apply_tags()


    def apply_tags(self):
        for rec in self:
            if rec.tags_to_affect_ids:
                if rec.invoice_line_ids:
                    for line in rec.invoice_line_ids:
                        to_be_not_deleted = []
                        if line.analytic_tag_ids:
                            to_be_not_deleted = line.analytic_tag_ids.filtered(lambda u: u.irremovable == True).mapped('id')
                        for tag in rec.tags_to_affect_ids:
                            to_be_not_deleted.append(tag.id)
                        # tags = rec.env['account.analytic.tag'].sudo().browse(to_be_not_deleted)
                        if to_be_not_deleted:
                            line.analytic_tag_ids = [(6, 0, to_be_not_deleted)]


    def duplicate_bc_attachment(self):
        self.ensure_one()
        if self.invoice_line_ids:
            if self.invoice_line_ids.sale_line_ids:
                order_id = self.invoice_line_ids.sale_line_ids.mapped('order_id')
                if order_id:
                    copied_attachments = []
                    order_attachments = self.env['ir.attachment'].search([('res_model', '=',order_id._name),('res_id', '=', order_id.id)])
                    if order_attachments:
                        self_attachements = self.env['ir.attachment'].search([('res_model', '=',self._name),('res_id', '=', self.id)])
                        if self_attachements:
                            copied_attachments = self_attachements.mapped('sale_attachement_id')
                        for r in order_attachments:
                            if r not in copied_attachments:
                                r.sudo().copy(
                                    {'res_model': self._name, 'res_id': self.id, 'sale_attachement_id': r.id})


    @api.depends('restrict_mode_hash_table', 'state')
    def _compute_show_reset_to_draft_button(self):
        super()._compute_show_reset_to_draft_button()
        for move in self:
            move.show_reset_to_draft_button = not move.restrict_mode_hash_table and move.state in ('posted', 'cancel', 'attente')
            for doc in move.edi_document_ids:
                if doc.edi_format_id._needs_web_services() \
                        and doc.attachment_id \
                        and doc.state in ('sent', 'to_cancel') \
                        and move.is_invoice(include_receipts = True) \
                        and doc.edi_format_id._is_required_for_invoice(move):
                    move.show_reset_to_draft_button = False
                    break

    @api.model
    def default_get(self, default_fields):
        # OVERRIDE
        values = super(AccountMove, self).default_get(default_fields)
        default_soustraitant = self._context.get('default_soustraitant', False)
        if default_soustraitant:
            journal_id = self.env['account.journal'].search(
                    [('journal_sous_traitant', '=', True), ('type', '=', 'purchase'),
                     ])
            if journal_id:
                values.update({'journal_id':journal_id[0].id })


        return values

    @api.model
    def _get_default_journal(self):
        journal = super(AccountMove, self)._get_default_journal()
        default_soustraitant = self._context.get('default_soustraitant', False)
        if default_soustraitant:
            journal_id = self.env['account.journal'].search([('journal_sous_traitant', '=', True), ('type', '=', 'purchase'),
                                                          ])
            if journal_id:
                journal = journal_id[0]

        return journal

    retenue_garantie = fields.Float('% Retenue de Garantie')
    invoice_date = fields.Date(default = fields.Date.context_today)

    sent_by_mail = fields.Boolean(string = "Envoyée par email", readonly = True)
    mask_report_partner_name = fields.Boolean('(Rapports) Masquer nom client ?')
    tech1_id = fields.Many2one('hr.employee', string = 'Tech 1')
    tech2_id = fields.Many2one('hr.employee', string = 'Tech 2')
    interim_ssl = fields.Char(string = 'Intérim/SST')

    tags_to_affect_ids = fields.Many2many('account.analytic.tag', string = 'Étiquettes analytiques',
                                          relation = 'account_move_account_analytic_tag_rel')

    partner_text_facturation = fields.Text(string='Texte de Facturation')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('attente','En Attente de validation'),
        ('posted', 'Open'),
        ('cancel', 'Cancelled')
        ], string='Invoice Status', readonly=True)
    type_facturation = fields.Selection(related='partner_id.type_facturation', store=True)
    show_confirm_button = fields.Boolean(compute='compute_show_confirm_button', store=True)
    followup_required = fields.Boolean(compute='compute_followup_required', string="Relance requise")
    modalite_paiement_id = fields.Many2one('modalite.paiement',string='Modalité de paiement')
    n_siret = fields.Char(string='N° de SIRET', related='partner_id.siret', store=True)
    sale_chantier_id = fields.Many2one('project.project', 'Chantier')
    chantier_analytic_account_id = fields.Many2one('account.analytic.account', related='sale_chantier_id.analytic_account_id', store=True, string='Compte analytique')
    nom_client_final = fields.Char('Nom/prénom')
    appart_client_final = fields.Char('N° appartement')
    ville_client_final = fields.Char('Ville')
    partner_address_1 = fields.Char("Adresse locataire/particulier")
    tel_client_final = fields.Char('Tél')
    code_postal = fields.Char('Code postal')
    civility = fields.Many2one('res.partner.title', 'Civilité client final')
    text_civility = fields.Many2one('res.partner.title', 'Civilité texte')
    code_service = fields.Char(string='Code Service')
    marche = fields.Char(string='Marché')
    line_chantier_id = fields.Many2one('project.project', compute="compute_line_chantier", store=True, string='line project')
    # line_chantier_id = fields.Many2one('project.project', string='Chantier')

    adress3 = fields.Text(string='Adresse 3')
    ##--##
    bilan_year = fields.Selection(string = "BILAN FISCAL", selection = [('2020', '2020'),
                                                                        ('2021', '2021'),
                                                                        ('2022', '2022'),
                                                                        ('2023', '2023'),
                                                                        ('2024', '2024'),
                                                                        ('2025', '2025'),
                                                                        ('2026', '2026'),
                                                                        ('2027', '2027'),
                                                                        ('2028', '2028'),
                                                                        ('2029', '2029'),
                                                                        ('2030', '2030')], required = False)

    ##--##

    date_realisation = fields.Datetime(string = "Date de realisation", store = True,
                                       compute = '_compute_date_realisation')

    gp_chantier_id = fields.Many2one(comodel_name = "project.group", string = "Group chantier", store = True,
                                     compute = '_compute_gp_chantier', inverse = '_set_gp_chantier', domain="[('id','in',project_group_ids)]")

    # group_chantier_id = fields.Many2one('project.group', string='Groupe chantier', domain="[('id','in',project_group_ids)]")
    project_group_ids = fields.Many2many('project.group',compute='compute_chantier_group_ids',  relation='account_move_project_groups_rel', store=True)
    st_amount_ht = fields.Float(compute="compute_st_amount_ht", store=True, string='Montant HT (ST)')
    conducteur_travaux_id = fields.Many2one(related="sale_chantier_id.conducteur_travaux_id", string="Conducteur des travaux", store=True)
    bc = fields.Char(string="BC client de l'avoir", related="reversed_entry_id.ref", store=True)


    @api.depends('invoice_line_ids', 'invoice_line_ids.sous_traitance', 'invoice_line_ids.price_subtotal')
    def compute_st_amount_ht(self):
        for record in self:
            if record.invoice_line_ids:
                record.st_amount_ht = sum(record.invoice_line_ids.filtered(lambda u: u.sous_traitance).mapped('price_subtotal'))


    def _post(self, soft=True):
        invoices = self.filtered(lambda r: r.invoice_date and r.move_type != 'entry')
        if invoices:
            for invoice in invoices:
                invoice.date = invoice.invoice_date
        res = super()._post(soft)
        return res

    @api.depends('line_chantier_id','line_chantier_id.group_ids')
    def compute_chantier_group_ids(self):
        for record in self:
            l = []
            if record.line_chantier_id:
                if record.line_chantier_id.group_ids:
                    record.project_group_ids = record.line_chantier_id.group_ids


    @api.depends('invoice_line_ids', 'invoice_line_ids.sale_line_ids', 'invoice_line_ids.sale_line_ids.date_realisation_so')
    def _compute_date_realisation(self):
        for rec in self:
            if rec.invoice_line_ids and rec.invoice_line_ids.sale_line_ids:
                date_realisation_so = rec.invoice_line_ids.mapped('sale_line_ids.date_realisation_so')
                if date_realisation_so:
                    date_realisation_so = list(filter(None, date_realisation_so))
                    if date_realisation_so:
                        rec.date_realisation = max(date_realisation_so)
                    else:
                        rec.date_realisation = False
                else:
                    rec.date_realisation = False
            else:
                rec.date_realisation =  False



    @api.depends('invoice_line_ids',
                 'invoice_line_ids.sale_line_ids',
                 'invoice_line_ids.sale_line_ids.order_id',
                 'invoice_line_ids.sale_line_ids.order_id.group_chantier_id')
    def _compute_gp_chantier(self):
        for rec in self:
            if rec.invoice_line_ids and rec.invoice_line_ids.sale_line_ids:
                gp_chantier_id = rec.invoice_line_ids.mapped('sale_line_ids.order_id.group_chantier_id')
                if gp_chantier_id:
                    rec.gp_chantier_id = gp_chantier_id[0].id
                else:
                    rec.gp_chantier_id = False
            else:
                rec.gp_chantier_id = False

    def _set_gp_chantier(self):
        for rec in self:
            # for invoice_line in rec.invoice_line_ids:
            #     for sale_line in invoice_line.sale_line_ids:
            #         for sale_order in sale_line.order_id:
            #             sale_order.group_chantier_id = rec.gp_chantier_id
            if rec.invoice_line_ids and rec.invoice_line_ids.sale_line_ids:
                gp_chantier_id = rec.invoice_line_ids.mapped('sale_line_ids.order_id.group_chantier_id')
                if gp_chantier_id and gp_chantier_id[0] != rec.gp_chantier_id:
                    raise ValidationError('Le groupe chantier choisi est différent du groupe chanier du bon de commande')


    @api.depends('company_id', 'invoice_filter_type_domain')
    def _compute_suitable_journal_ids(self):
        for m in self:
            print('_compute_suitable_journal_ids', m.invoice_filter_type_domain)
            journal_type = m.invoice_filter_type_domain
            default_soustraitant = self._context.get('default_soustraitant', False)

            company_id = m.company_id.id or self.env.company.id

            if journal_type and  default_soustraitant :
                domain = [('company_id', '=', company_id), ('type', '=', journal_type), ('journal_sous_traitant', '=', True)]
            elif journal_type and not default_soustraitant:
                domain = [('company_id', '=', company_id), ('type', '=', journal_type)]

            else:
                domain = [('company_id', '=', company_id), ('type', 'not in', ('sale', 'purchase'))]

            m.suitable_journal_ids = self.env['account.journal'].search(domain)

    @api.depends('line_ids', 'line_ids.analytic_account_id', 'state')
    def compute_line_chantier(self):
        for rec in self:
            if rec.line_ids:
                if rec.line_ids.filtered(lambda r:r.analytic_account_id) and \
                        len(list(set(rec.line_ids.filtered(lambda r:r.analytic_account_id).mapped('analytic_account_id')))) == 1:

                    line_chantier_id = self.env['project.project'].search([('analytic_account_id', '=', rec.line_ids.mapped('analytic_account_id')[0].id),
                                                                           '|',('active', '=', True), ('active', '=', False)])
                    if line_chantier_id:
                        rec.line_chantier_id = line_chantier_id[0].id
                    else:
                        rec.line_chantier_id = False
                else:
                    rec.line_chantier_id = False
            else:
                rec.line_chantier_id = False

    def get_origin_sale_infos(self):
        for rec in self:
            if rec.invoice_origin:
                origin_sale = self.env['sale.order'].search([('name', '=', rec.invoice_origin)])
                if origin_sale:
                    return origin_sale

    def compute_followup_required(self):
        for rec in self:
            if rec.move_type in  ('out_invoice', 'out_refund', 'out_receipt') and \
                rec.invoice_date_due and rec.invoice_date_due <= fields.Date.context_today(self) and rec.payment_state in ('not_paid', 'partial'):
                rec.followup_required = True
            else:
                rec.followup_required = False

    def action_invoice_followup_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """

        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template= self.env.ref('account_extend.email_template_invoice_followup')
        lang = self.env.context.get('lang')
        # c = False
        # if self.custom_report_file:

        # template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]

        ctx = {
            'default_model': 'account.move',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template),
            'default_template_id': template.id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            # 'custom_layout': "mail.mail_notification_paynow",
            # 'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'model_description': self.with_context(lang = lang).type_name,
        }
        # if c:
        #     ctx['default_attachment_ids'] = [(6,0, c.ids)]


        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    @api.depends('state', 'move_type')
    def compute_show_confirm_button(self):
        for rec in self:
            rec.show_confirm_button = False
            if rec.move_type in ('out_invoice', 'out_refund', 'out_receipt'):
                if rec.state == 'attente':
                    rec.show_confirm_button = True
                else:
                    rec.show_confirm_button = False
            else:
                if rec.state == 'draft':
                    rec.show_confirm_button = True
                else:
                    rec.show_confirm_button = False


    def action_en_attente(self):
        self.write({'state':'attente'})

    @api.onchange('partner_id')
    def onchange_partner(self):
        if self.partner_id:
            self.partner_text_facturation = self.partner_id and self.partner_id.texte_facturation
            self.modalite_paiement_id = self.partner_id and self.partner_id.modalite_paiement_id and self.partner_id.modalite_paiement_id.id or False

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountMove, self).create(vals_list)
        for move in res:
            if move.move_type in ('out_invoice', 'out_refund', 'out_receipt') and move.partner_id:
                move.partner_text_facturation = move.partner_id.texte_facturation
        return res

    def write(self, vals):
        res = super(AccountMove, self).write(vals)

        for rec in self:
            if vals.get('sale_chantier_id', False):
                chantier_id = rec.env['project.project'].browse(vals.get('sale_chantier_id'))
                if chantier_id:
                    if rec.line_ids:
                        for i in rec.line_ids:
                            i.write({'analytic_account_id': chantier_id.analytic_account_id.id})

            if vals.get('sale_chantier_id') == False:
                if rec.line_ids and not rec.sale_chantier_id:
                     rec.line_ids.write({'analytic_account_id': False})

            if vals.get('partner_id', False) and not vals.get('partner_text_facturation', False):
                if rec.partner_id.texte_facturation != rec.partner_text_facturation:
                    rec.partner_text_facturation =  rec.partner_id.texte_facturation
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    line_chantier_id = fields.Many2one('project.project', compute="compute_line_chantier",  store=True)
    unique_tax_id = fields.Many2one('account.tax', compute='compute_unique_tax', store=True)
    sous_traitance = fields.Boolean(string="Sous traitance")
    group_id = fields.Many2one(comodel_name="project.group",related='move_id.gp_chantier_id', string="Groupe chantier", store=True)

    @api.depends('tax_ids')
    def compute_unique_tax(self):
        for rec in self:
            if rec.tax_ids and len(rec.tax_ids)==1:
                rec.unique_tax_id = rec.tax_ids[0].id
            else:
                rec.unique_tax_id = False


    @api.depends('analytic_account_id', 'move_id', 'move_id.line_chantier_id')
    def compute_line_chantier(self):
        for rec in self:
            move_project = False

            if rec.analytic_account_id:
                project = self.env['project.project'].search(
                        [('analytic_account_id', '=', rec.analytic_account_id.id),
                         '|', ('active', '=', True), ('active', '=', False)])
                if project:
                    rec.line_chantier_id = project[0].id
                else:
                    rec.line_chantier_id = False
            elif rec.move_id.line_chantier_id:
                rec.line_chantier_id = rec.move_id.line_chantier_id.id
            else:
                rec.line_chantier_id = False

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountMoveLine, self).create(vals_list)
        for rec in res:
            if rec.partner_id and rec.partner_id.category_id and  rec.partner_id.category_id.analytic_tag_id:
                rec.write({'analytic_tag_ids':[(4, t.analytic_tag_id.id) for t in rec.partner_id.category_id]})
            if rec.move_id.sale_chantier_id :
                rec.analytic_account_id = rec.move_id.sale_chantier_id.analytic_account_id.id
        return res

    def write(self, vals):
        res = super(AccountMoveLine, self).write(vals)
        if res and vals.get('partner_id', False):
            for rec in self:
                if rec.partner_id and rec.partner_id.category_id and  rec.partner_id.category_id.analytic_tag_id:
                    rec.write({'analytic_tag_ids':[(4, t.analytic_tag_id.id) for t in rec.partner_id.category_id]})

        if res and vals.get('analytic_account_id', False):
            for rec in self:
                if rec.analytic_account_id and rec.move_id.sale_chantier_id and rec.move_id.chantier_analytic_account_id != rec.analytic_account_id:
                    rec.chantier_analytic_account_id = rec.move_id.chantier_analytic_account_id.id
        return res


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(SaleOrder, self).onchange_partner_id()
        self.partner_invoice_id = self.partner_id




    def _prepare_invoice(self):
        res = super(SaleOrder, self)._prepare_invoice()
        if self.chantier_id:
            res['sale_chantier_id'] = self.chantier_id.id
        if self.tech1_id:
            res['tech1_id'] = self.tech1_id.id
        if self.tech2_id:
            res['tech2_id'] = self.tech2_id.id

        res['interim_ssl'] = self.interim_ssl
        res['nom_client_final'] = self.nom_client_final
        res['ville_client_final'] = self.ville_client_final
        res['partner_address_1'] = self.partner_address_1
        res['tel_client_final'] = self.tel_client_final
        res['code_postal'] = self.code_postal
        res['civility'] = self.civility
        res['adress3'] = self.adress3
        res['text_civility'] = self.text_civility and self.text_civility.id or False

        res['name'] = '/'

        return res


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    journal_sous_traitant = fields.Boolean(string='Facture des sous-traitants')

    def name_get(self):
        res = super(AccountJournal, self).name_get()
        for journal_name in res:
            name = journal_name[1]
            index = res.index(journal_name)
            journal_id = self.env['account.journal'].browse(journal_name[0])

            if journal_id.code:
                name = "(%s) %s" % (journal_id.code, name)
            res[index] = (journal_name[0], name)
        return res


class AccountAnalyticTag(models.Model):
    _inherit = 'account.analytic.tag'

    irremovable = fields.Boolean('A ne pas supprimer', help="Tag utilisaer pour séparrer les partenaires")

    def unlink(self):
        for rec in self:
            if rec.irremovable:
                raise ValidationError('Vous ne pouvez pas supprimer ce tag')
        return super(AccountAnalyticTag, self).unlink()

class ResPartnerCategory(models.Model):
    _inherit = 'res.partner.category'

    analytic_tag_id = fields.Many2one('account.analytic.tag', 'Etiquette analytique')
    irremovable = fields.Boolean('A ne pas supprimer', help="Tag utilisaer pour séparrer les partenaires")

    def unlink(self):
        for rec in self:
            if rec.irremovable:
                raise ValidationError('Vous ne pouvez pas supprimer ce tag')
        return super(ResPartnerCategory, self).unlink()

    @api.model
    def create(self, vals):
        res = super(ResPartnerCategory, self).create(vals)
        if res and not res.analytic_tag_id:
            tag_id = self.env['account.analytic.tag'].sudo().create({'name': res.name})
            res.analytic_tag_id = tag_id.id

        return res

    def write(self, vals):
        res = super(ResPartnerCategory, self).write(vals)
        if res:
            for rec in self:
                if not rec.analytic_tag_id:

                    tag_id = self.env['account.analytic.tag'].create({'name': rec.name})
                    rec.analytic_tag_id = tag_id.id

        return res


