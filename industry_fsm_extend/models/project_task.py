# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'


    fsm_state = fields.Selection([('draft', 'Nouveau'), ('confirm', 'Validé'), ('done', 'Fait')], default='draft')
    # fsm_sales_ids = fields.One2many('sale.order', 'fsm_task_id', 'Devis/commande')
    # fsm_sales_count = fields.Integer('Devis/commande', compute='compute_fsm_sales_count', store=True)
    project_user_id = fields.Many2one('res.users', related='project_id.user_id', store=True, string='Responsable chantier')

    # @api.depends('fsm_sales_ids')
    # def compute_fsm_sales_count(self):
    #     for rec in self:
    #         if rec.fsm_sales_ids:
    #             rec.fsm_sales_count = len(rec.fsm_sales_ids)
    #         else:
    #             rec.fsm_sales_count =0
    #
    # def prepare_sale_val(self):
    #     self.ensure_one()
    #     return {'partner_id': self.partner_id.id,
    #             'date_order': self.planned_date_begin or fields.Datetime.now(),
    #             'origin': self.name,
    #             'chantier_id': self.project_id.id,
    #             'fsm_task_id': self.id,
    #             }

    def fsm_confirm_action_done(self):
        self.write({'fsm_state': 'done', 'fsm_done': True})
    #
    # def fsm_confirm_action(self):
    #     self.write({'fsm_state': 'confirm'})
    #     for res in self:
    #         if res.is_fsm and res.partner_id:
    #             vals = res.prepare_sale_val()
    #             print('vvvvv', vals)
    #             sale_id = self.env['sale.order'].sudo().create(vals)
    #             # res.sale_order_id = sale_id.id


    # def fsm_sales_action(self):
    #     self.ensure_one()
    #     return {'type': 'ir.actions.act_window',
    #             'view_mode': 'tree,form',
    #             'res_model': 'sale.order',
    #             'target': 'current',
    #             'domain':[('fsm_task_id', '=', self.id)],
    #             'context': {'default_chantier_id': self.project_id.id,
    #                         'default_partner_id': self.partner_id.id,
    #                         'default_fsm_task_id': self.id,
    #                         }}


    @api.model
    def create(self, vals):
        res = super(ProjectTask, self).create(vals)
        if self.env.context.get('fsm_mode', False):
            res.project_id.is_fsm = True

        return res

