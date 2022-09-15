# -*- coding: utf-8 -*-

import base64
import requests
import logging
import uuid
from odoo import models, fields, api
from odoo.exceptions import ValidationError
_logger = logging.getLogger(__name__)

class Company(models.Model):
    _inherit = 'res.company'

    chorus_url = fields.Char("URL")
    GatewayClientId = fields.Char("GatewayClientId")
    MachineName = fields.Char("MachineName")
    AccessKey = fields.Char("AccessKey")
    OneWayAPI = fields.Boolean("OneWayAPI")
    TemplateId = fields.Char("TemplateId")
    APIClientId = fields.Char("APIClientId")


class AccountMove(models.Model):
    _inherit = 'account.move'

    chorus_sent = fields.Boolean("Envoyée à chorus", readonly=True)



    def get_token(self,url,APIClientId,AccessKey):
        url = url+'/api/login/ac'
        data = {
            "APIClientId":APIClientId,
         # "GatewayClientId": GatewayClientId,
         # "MachineName": MachineName,
         "AccessKey": AccessKey,
         # "OneWayAPI": OneWayAPI,
        }
        res = requests.post(url, json=data)
        if res.status_code == 200:
            return res.text
        else:
            return False

    def masse_facturation_chorus(self):
        for rec in self:
            if rec.type_facturation == 'chorus' and rec.state == 'posted':
                rec.facturation_chorus()


    def facturation_chorus(self):
        self.ensure_one()
        send_url = self.company_id.chorus_url+'/api/clt/documents/send'
        GatewayClientId = self.company_id.GatewayClientId
        MachineName = self.company_id.MachineName
        AccessKey = self.company_id.AccessKey
        OneWayAPI = self.company_id.OneWayAPI
        TemplateId = self.company_id.TemplateId
        APIClientId = self.company_id.APIClientId
        token = self.get_token(self.company_id.chorus_url,APIClientId,AccessKey)
        headers = {'Authorization': 'Bearer ' + token}
        report_name = ""
        # pdf = self.env.ref('account_extend.gecop_invoice_siret_report_id').sudo()._render_qweb_pdf([self.id], report_name)[0]
        # if not self.custom_report_file:
        self.print_custom_report()
        if self.custom_report_file:
            pdf = self.custom_report_file
            file = pdf
        else:
            pdf = self.env.ref('account_extend.gecop_invoice_siret_report_id').sudo()._render_qweb_pdf([self.id],
                                                                                                       report_name)[0]
            file = base64.b64encode(pdf).decode('utf-8')
        # file = base64.b64encode(pdf).decode('utf-8')

        data = {
            "DocumentId": str(uuid.uuid1()),
            "TemplateId": TemplateId,
            "FileName": f"{self.name.replace('/','')}.pdf",
            "FileSize": len(pdf),
            "FileContent": file,
            "Variables": ""
        }
        res = requests.post(send_url, json=data, headers=headers)

        if res.status_code == 200:
            self.chorus_sent = True

        else:
            print('rrrrrrrres chorus', res)
            _logger.info("chorus res %s, status_code %s : %s", res, res.status_code, res.text)
            message = 'Echec transfert! \n' \
                      'chorus res %s, status_code %s : %s"'
            raise ValidationError('Echec transfert! \n chorus res %s, status_code %s : %s"'%( res, res.status_code, res.text))

        return res.status_code

