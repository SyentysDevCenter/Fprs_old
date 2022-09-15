# -*- coding: utf-8 -*-

from odoo import models, fields, api

class MailCompose(models.TransientModel):
    _inherit = 'mail.compose.message'

    def action_send_mail(self):
        res = super(MailCompose, self).action_send_mail()
        if self.model == 'account.move':
            active_record = self.env[self.model].browse(self.res_id)
            if active_record:
                active_record.write({'sent_by_mail': True})
        return res