# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'


    def onchange_template_id(self, template_id, composition_mode, model, res_id):
        res = super(MailComposer, self).onchange_template_id(template_id, composition_mode, model, res_id)
        if res and res.get('value', False):
            if model == 'account.move':
                active_ids = self.env.context.get('active_ids')
                if len(active_ids) == 1:
                    active_record =  self.env[model].browse(res_id)
                    if active_record:
                        if not active_record.custom_report_file:
                            active_record.print_custom_report()
                        if active_record.custom_report_file:
                            d = {'name': "%s.pdf" % active_record.name, 'res_id': False,
                                     'res_model': 'account.move', 'datas': active_record.custom_report_file}
                            c = self.env['ir.attachment'].sudo().create(d)
                            if c:
                                res['value']['attachment_ids'] = [(6 ,0, c.ids)]
        return res


    def render_message(self, res_ids):
        s = super(MailComposer, self).render_message(res_ids)
        if self.model == 'account.move':
            for r in s:
                related_in = self.env['account.move'].browse(r)
                if related_in:
                    if not related_in.custom_report_file:
                        related_in.print_custom_report()
                    if related_in.custom_report_file:
                        if s[r].get('attachments'):
                            s[r].get('attachments').pop(0)
                        else:
                            s[r]['attachments'] = []
                        s[r].get('attachments').append((related_in.name, related_in.custom_report_file))

        return s



class AccountInvoiceSend(models.TransientModel):
    _inherit = 'account.invoice.send'

    def send_and_print_action(self):
        res = super().send_and_print_action()
        self.invoice_ids.write({'sent_by_mail': True})
        return res

