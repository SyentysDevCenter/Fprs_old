# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError

from datetime import timedelta, datetime


class MailFollowers(models.Model):
    _inherit = 'mail.followers'

    @api.model
    def create(self, values):
        res = super(MailFollowers, self).create(values)
        if res.res_model == "project.task" and res.res_id:
            task = self.env['project.task'].search([('id', '=', res.res_id)])
            followers = self.search([('res_model', '=', "project.task"), ('res_id', '=', res.res_id)])
            intervenants = task.intervenant_ids.mapped('partner_id')
            for follower in followers:
                if not (follower.partner_id == task.user_id.partner_id or follower.partner_id == task.create_uid.partner_id or follower.partner_id in intervenants):
                    follower.unlink()
        return res


class ProjectTask(models.Model):
    _inherit = 'project.task'

    @api.model
    def _read_group_user_ids(self, users, domain, order):
        if self.env.context.get('fsm_mode'):
            domain_task = [
                              ('create_date', '>', datetime.now() - timedelta(days=30)),
                              ('is_fsm', '=', True),
                              ('user_id', '!=', False)] + domain
            recently_created_tasks = self.env['project.task'].search(domain_task)
            # search_domain = ['|', '|', ('id', 'in', users.ids),
            #                  ('groups_id', 'in', self.env.ref('industry_fsm.group_fsm_user').id),
            #                  ('id', 'in', recently_created_tasks.mapped('user_id.id'))]
            search_domain = [
                ('groups_id', 'in', self.env.ref('industry_fsm.group_fsm_user').id),
                ('id', 'in', recently_created_tasks.mapped('user_id.id'))]
            print('search_domain', search_domain)
            print('usersusers', users)
            print('recently_created_tasks', recently_created_tasks)
            return users.search(search_domain, order=order)
        return users

    fsm_sale_id = fields.Many2one('sale.order', 'Bon de commande', ondelete='cascade')
    fsm_state = fields.Selection(
        [('draft', 'Nouveau'), ('attente', 'En attente de validation'), ('done', 'Fait'), ('confirm', 'Validé')],
        string="Etat",
        default='draft')
    fsm_status_id = fields.Many2one('project.task.status', 'ETAT INTER')
    fsm_status_is_inter_4 = fields.Boolean(related='fsm_status_id.is_inter_4', store=True)
    fsm_status_is_inter_8 = fields.Boolean(related='fsm_status_id.is_inter_8', store=True)

    bailleur_id = fields.Many2one('res.partner', 'Bailleur')
    en_attente = fields.Boolean('En attente', compute="compute_en_attente", store=True)
    fsm_sav = fields.Boolean('SAV', default=False)
    fsm_sav_ids = fields.One2many('project.task', 'fsm_id', 'SAV', domain=[('fsm_sav', '=', True)])
    fsm_id = fields.Many2one('project.task', "Intervention d'origine")
    fsm_sav_count = fields.Integer('SAV', compute="compute_fsm_sav_count", store=True)
    is_fsm = fields.Boolean(related='', search='', default=False)
    nom_client_final = fields.Char('Nom/prénom', related='fsm_sale_id.nom_client_final', store=True)
    appart_client_final = fields.Char('N° appartement', related='fsm_sale_id.appart_client_final', store=True)
    ville_client_final = fields.Char('Ville', related='fsm_sale_id.ville_client_final', store=True)
    tel_client_final = fields.Char('Tél', related='fsm_sale_id.tel_client_final', store=True)
    code_postal_final = fields.Char('Code postal', related='fsm_sale_id.code_postal', store=True)
    partner_address_1 = fields.Char("Ligne d'adresse 1", related='fsm_sale_id.partner_address_1', store=True)
    has_edit_acces = fields.Boolean(compute='compute_has_edit_acces')
    planned_date_begin = fields.Datetime("Start date", tracking=True)
    planned_date_end = fields.Datetime("End date", tracking=True)
    conducteur_travaux_id = fields.Many2one('res.users', related='project_id.conducteur_travaux_id', store=True)
    client_order_ref = fields.Char(string='N° BC client', related='fsm_sale_id.client_order_ref')
    intervenant_ids = fields.Many2many('res.users', string='INTERVENANTS SUPPL', relation='inetrvenant_task_rel')
    last_state = fields.Boolean(string='Etat finale', related='fsm_status_id.last_state',
                                store=True)
    fournitures_info_divers = fields.Html(string='FOURNITURES/Info divers')
    date_realisation = fields.Datetime(string='Date de réalisation')
    interim_ssl = fields.Char(string='Intérim/SST')
    email_destination_ids = fields.Many2many(comodel_name="res.partner", relation="task_email_dest_rel",
                                             column1="task_id", column2="destination_id", string="", )

    is_invoiced = fields.Boolean(string="Facturé", compute="_compute_is_invoiced")



    # @api.onchange('intervenant_ids')
    # def onchange_intervenant(self):
    #     if self.intervenant_ids:
    #         partners = self.intervenant_ids.mapped('partner_id.id')
    #         self.message_subscribe(partners)

    @api.depends('fsm_sale_id', 'fsm_sale_id.invoice_ids')
    def _compute_is_invoiced(self):
        for task in self:
            if len(task.fsm_sale_id.invoice_ids) > 0:
                task.is_invoiced = True

            else:
                task.is_invoiced = False

    def change_status(self):
        for rec in self:
            if rec.is_invoiced:
                raise ValidationError("L'intervention est déjà facturé \nVous ne pouvez pas la remettre à nouveau !!")
            else:
                rec.fsm_state = 'draft'


    def fsm_special_validate(self):
        self.write({'fsm_state': 'confirm'})
        for rec in self:
            if not rec.date_realisation :
                rec.date_realisation = fields.Datetime.now()
    #
    @api.onchange('fsm_sale_id')
    def onchange_fsm_sale_id(self):
        if self.fsm_sale_id:
            self.partner_id = self.fsm_sale_id.partner_id.id
            self.project_id = self.fsm_sale_id.chantier_id and self.fsm_sale_id.chantier_id.id or False
            self.bailleur_id = self.fsm_sale_id.bailleur_id and self.fsm_sale_id.bailleur_id.id or False

    @api.onchange('project_id')
    def onchange_project(self):
        if self.project_id and self.project_id.bailleur_id:
            self.bailleur_id = self.project_id.bailleur_id.id
        if self.project_id and self.project_id.analytic_account_id:
            self.analytic_account_id = self.project_id.analytic_account_id.id
        if self.project_id and self.fsm_sale_id:
            if self.project_id.partner_id and self.project_id.partner_id != self.fsm_sale_id.partner_id:
                self.fsm_sale_id = False

    @api.depends('user_id')
    def compute_has_edit_acces(self):
        for rec in self:
            if self.env.user.user_has_groups('industry_fsm.group_fsm_manager, project.group_project_manager'):
                rec.has_edit_acces = True
            else:
                rec.has_edit_acces = False

    @api.model
    def create(self, vals):
        res = super(ProjectTask, self).create(vals)
        if res.intervenant_ids:

            partners = res.intervenant_ids.mapped('partner_id.id')
            res.message_subscribe(partners)
            for follower in res.message_follower_ids:

                if follower.partner_id != res.user_id.partner_id and follower.partner_id != res.create_uid.partner_id and follower.partner_id.id not in partners:
                    res.message_unsubscribe([follower.partner_id.id])

        if vals.get('fsm_sale_id', False):
            sale = self.env['sale.order'].browse(vals.get('fsm_sale_id'))
            if sale:
                res.interim_ssl = sale.interim_ssl

        if res.fsm_sale_id and vals.get('fsm_status_id', False):
            statut = vals['fsm_status_id']
            res.fsm_sale_id.fsm_status_id = statut
        return res

    def write(self, values):
        result = super(ProjectTask, self).write(values)
        if values.get('intervenant_ids', False):
            for rec in self:
                partners = rec.intervenant_ids.mapped('partner_id.id')
                rec.message_subscribe(partners)
                for follower in rec.message_follower_ids:

                    if follower.partner_id != rec.user_id.partner_id and follower.partner_id != rec.create_uid.partner_id and follower.partner_id.id not in partners:
                        rec.message_unsubscribe([follower.partner_id.id])

        if values.get('fsm_sale_id', False):
            for rec in self:
                sale = rec.fsm_sale_id
                if sale:
                    rec.interim_ssl = sale.interim_ssl
        for rec in self:
            if values.get('fsm_status_id', False):
                if rec.fsm_sale_id:
                    rec.fsm_sale_id.fsm_status_id = rec.fsm_status_id.id
        return result

    def _sms_get_number_fields(self):
        """ This method returns the fields to use to find the number to use to
        send an SMS on a record. """
        return ['mobile', 'phone']

    def fsm_sav_action(self):
        self.ensure_one()
        context = {'fsm_mode': True,
                   'fsm_sav': True,
                   'show_address': True,
                   'search_default_my_tasks': True,
                   'search_default_planned_future': True,
                   'search_default_planned_today': True,
                   'fsm_task_kanban_whole_date': False,
                   'default_is_fsm': True,
                   'default_fsm_sav': True,
                   'default_fsm_id': self.id,
                   'default_partner_id': self.partner_id.id,
                   'default_partner_email': self.partner_id.email,
                   'default_bailleur_id': self.bailleur_id and self.bailleur_id.id or False,
                   'default_project_id': self.project_id and self.project_id.id
                   }

        return {'type': 'ir.actions.act_window',
                'name': "Interventions",
                'res_model': 'project.task',
                'view_mode': 'tree,form,map,kanban,gantt,calendar,activity',
                'domain': [('fsm_id', '=', self.id), ('fsm_sav', '=', True)],
                'context': context,
                'target': 'current',
                }

    @api.depends('fsm_sav_ids')
    def compute_fsm_sav_count(self):
        for rec in self:
            if rec.fsm_sav_ids:
                rec.fsm_sav_count = len(rec.fsm_sav_ids)
            else:
                rec.fsm_sav_count = 0

    @api.depends('planned_date_begin')
    def compute_en_attente(self):
        for rec in self:
            if not rec.planned_date_begin:
                rec.en_attente = True
            else:
                rec.en_attente = False

    def fsm_confirm_action_done(self):
        if any(not l.last_state for l in self):
            raise UserError("L'état des interventions n'est pas finale!")
        self.write({'fsm_state': 'done', 'fsm_done': True})

    def fsm_mettre_en_attente(self):
        self.write({'fsm_state': 'attente',
                    'date_realisation': datetime.now(),
                    })

    def fsm_mettre_a_nouveau_action(self):
        self.write({'fsm_state': 'draft',
                    'fsm_done': False})

    def fsm_report(self):
        for rec in self:
            rec.planned_date_begin = False
            rec.planned_date_end = False

    def fsm_confirm_action(self):
        if any(not l.last_state for l in self):
            raise UserError("L'état des interventions n'est pas finale!")
        self.write({'fsm_state': 'confirm'})

    def action_intervention_send(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self.env['ir.model.data'].xmlid_to_res_id('sale_fsm_extend.email_template_edi_intervention',
                                                                raise_if_not_found=False)
        # ${object.partner_id != False and object.partner_id.id}
        partners = []
        if self.email_destination_ids:
            partners.append(self.email_destination_ids.mapped("id"))
        if self.partner_id and self.partner_id.email:
            partners.append(self.partner_id.id)
        ctx = {
            'default_model': 'project.task',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_partner_id': self.partner_id.id,
            # 'default_partner_ids': partners ,
            'default_partner_ids': self.email_destination_ids.mapped("id"),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_light",
            'force_email': True,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }


class ProjetTaskStatus(models.Model):
    _name = 'project.task.status'

    code = fields.Char('Etat')
    name = fields.Char(string='Descriptif', required=True)
    last_state = fields.Boolean(string='Etat finale')
    is_inter_4 = fields.Boolean(string='Inter 4')
    is_inter_8 = fields.Boolean(string='Inter 8')


class Project(models.Model):
    _inherit = 'project.project'

    conducteur_travaux_id = fields.Many2one('res.users', domain="[('charge_affaire', '=', True)]")

