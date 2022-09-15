# -*- coding: utf-8 -*-


from odoo import api, fields, models
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # def write(self, vals):
    #     res = super(SaleOrder, self).write(vals)
    #     for rec in self:
    #         if vals.get('message_main_attachment_id', False) or vals.get('fsm_task_ids', self):
    #             sale_attachments = self.env['ir.attachment'].search([('res_model', '=', rec._name),('res_id','=', rec.id)])
    #             if sale_attachments:
    #                 if rec.fsm_task_ids:
    #                     for task in rec.fsm_task_ids:
    #                         task_attachments = self.env['ir.attachment'].search(
    #                                 [('res_model', '=', task._name), ('res_id', '=', task.id)])
    #                         attachement = sale_attachments - (task_attachments and task_attachments.mapped('origin_attachement_id') or self.env['ir.attachment'])
    #                         for at in attachement:
    #                             new_attachement = at.copy({'origin_attachement_id': at.id})
    #                             new_attachement.res_model = task._name
    #                             new_attachement.res_id = task.id
    #
    #     return res

