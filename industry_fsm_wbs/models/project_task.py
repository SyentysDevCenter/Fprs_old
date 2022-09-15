# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    wbs_fsm_id = fields.Many2one('project.wbs', 'Ligne BDP')
    lot_id = fields.Many2one('ao.lot', related='wbs_fsm_id.lot_id', store=True)

    def prepare_sale_val(self):
        vals = super(ProjectTask, self).prepare_sale_val()
        vals['wbs_fsm_id'] = self.wbs_fsm_id and self.wbs_fsm_id.id or False
        return vals




    def fsm_sales_action(self):
        action = super(ProjectTask, self).fsm_sales_action()
        action['context']['default_wbs_fsm_id'] = self.wbs_fsm_id and self.wbs_fsm_id.id or False
        return action



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    wbs_fsm_id = fields.Many2one('project.wbs', 'Ligne BDP')
    lot_id = fields.Many2one('ao.lot', related='wbs_fsm_id.lot_id', store=True)
