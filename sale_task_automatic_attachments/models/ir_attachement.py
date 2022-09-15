# -*- coding: utf-8 -*-


from odoo import api, fields, models
from odoo.exceptions import UserError




class IrAttachement(models.Model):
    _inherit = 'ir.attachment'

    origin_attachement_id = fields.Many2one('ir.attachment')

    def unlink(self):
        for rec in self:
            if rec.res_model == 'project.task':
                if rec.origin_attachement_id:
                    other_attachement = rec.origin_attachement_id
                    task_attachement = self.env['ir.attachment'].search([('origin_attachement_id', '=', rec.origin_attachement_id.id)])
                    self |= other_attachement
                    self |= task_attachement
            if rec.res_model == 'sale.order':
                task_attachement = self.env['ir.attachment'].search(
                        [('origin_attachement_id', '=', rec.id)])
                self |= task_attachement

        res = super(IrAttachement, self).unlink()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        res = super(IrAttachement, self).create(vals_list)

        for rec  in res:
            if rec.res_model == 'project.task' and not self.env.context.get('check_origin', False):
                task_id = self.env['project.task'].sudo().browse(rec.res_id)
                if task_id:
                    related_sale = task_id.fsm_sale_id
                    k = {}
                    if related_sale:
                        # k = vals
                        # k['res_model'] = related_sale._name
                        # k['res_id'] = related_sale.id
                        new_attachement = rec.sudo().with_context({'check_origin_task':rec.res_id}).copy({'res_model':related_sale._name, 'res_id': related_sale.id })
                        # new_attachement = self.env['ir.attachment'].sudo().with_context({'check_origin_task':vals['res_id']}).create(k)
                        rec.origin_attachement_id = new_attachement.id
            if rec.res_model == 'sale.order':
                sale_id = self.env['sale.order'].sudo().browse(rec.res_id)
                if sale_id:
                    related_tasks = sale_id.fsm_task_ids

                    if related_tasks:
                        origin_task = self.env.context.get('check_origin_task', False)
                        for task in related_tasks :
                            if task.id != origin_task:
                                # k['res_model'] = task._name
                                # k['res_id'] = related_sale.id
                                rec.sudo().with_context({'check_origin':True}).copy({'res_model':task._name, 'res_id':task.id,  'origin_attachement_id': rec.id})
                                # new_attachement = self.env['ir.attachment'].sudo().create(k)
                                # vals['origin_attachement_id'] = new_attachement.id

        return res




    # def _sale_task_duplicate_attachment(self):
    #     today = fields.Date.today()
    #     sale_model_name = 'sale.order'
    #     task_model_name = 'project.task'
    #
    #     _attachments = self.env['ir.attachment'].sudo().search([])
    #     today_attachment = _attachments.filtered(lambda u: u.create_date.strftime('%Y-%m-%d') == today.strftime('%Y-%m-%d'))
    #     sale_today_attachments = today_attachment.filtered(lambda u: u.res_model == sale_model_name and u.shared == False)
    #     task_today_attachments = today_attachment.filtered(lambda u: u.res_model == task_model_name and u.shared == False)
    #
    #
    #     if sale_today_attachments:
    #         for at in sale_today_attachments:
    #             related_sale = self.env['sale.order'].sudo().browse(at.res_id)
    #             if related_sale:
    #
    #                 if related_sale.fsm_task_ids:
    #                     at.shared = True
    #                     for t in related_sale.fsm_task_ids:
    #                         new = at.copy()
    #                         new.res_model = task_model_name
    #                         new.res_id = t.id
    #
    #     if task_today_attachments:
    #         for att in task_today_attachments:
    #             related_task = self.env['project.task'].sudo().browse(att.res_id)
    #             if related_task:
    #                 if related_task.fsm_sale_id:
    #                     att.shared = True
    #                     new1 = att.copy()
    #                     new1.res_model = sale_model_name
    #                     new1.res_id = related_task.fsm_sale_id.id


