# -*- coding: utf-8 -*-
import io
import base64
from PIL import Image
import PIL.PdfImagePlugin   # activate PDF support in PIL
from odoo import models, fields, api
from PyPDF2 import PdfFileMerger
from odoo.tools import pdf
import PyPDF2
from io import BytesIO
from reportlab.pdfgen import canvas
from PyPDF2 import  PdfFileReader, PdfFileWriter
from reportlab.lib.utils import ImageReader
from PyPDF2.pdf import PageObject

class AccountMove(models.Model):
    _inherit = 'account.move'

    custom_report_file = fields.Binary("Rapport généré", attachment=True, copy=False)
    invoice_report_model_id = fields.Many2one('ir.actions.report', string="Modèle d'impression", domain="[('model', '=', 'account.move')]")



    @api.model
    def create(self, vals):
        res = super(AccountMove, self).create(vals)
        if vals.get('partner_id'):
            partner = self.env['res.partner'].sudo().browse(vals.get('partner_id'))
            if partner:
                if partner.invoice_report_model_id:
                    res.invoice_report_model_id = partner.invoice_report_model_id.id

        return res


    def write(self, vals):
        res = super(AccountMove, self).write(vals)
        for rec in self:
            if vals.get('partner_id'):
                rec.invoice_report_model_id =  rec.partner_id.invoice_report_model_id.id
        return res

    def action_invoice_sent(self):
        sup = super(AccountMove, self).action_invoice_sent()
        sup['context']['default_is_print'] = False
        return sup

    def action_post(self):

        res = super(AccountMove, self).action_post()
        for rec in self:
            if rec.move_type == 'out_invoice':
                rec.print_custom_report()
        return res


    def print_custom_report(self):
        self.custom_report_file = False
        pdfs = []

        custom_invoice = self.env.ref('gecop_model_reports.gecop_invoice_report_id')
        if self.partner_id.invoice_report_model_id:
            invoice_report = self.partner_id.invoice_report_model_id
        elif custom_invoice:
            invoice_report = custom_invoice
        else:
            invoice_report = self.env.ref('account.account_invoices', raise_if_not_found=True)
        invoice_pdf, _ = invoice_report._render_qweb_pdf(self.id)
        if invoice_pdf:
            pdfs.append(invoice_pdf)

        if self.invoice_line_ids:
            if self.invoice_line_ids.sale_line_ids:
                sale_order_id = self.invoice_line_ids.sale_line_ids.mapped('order_id')
                # sale_rep = self.env.ref('gecop_model_reports.sale_report_first')
                if sale_order_id:
                    if sale_order_id.partner_id.sale_report_model_id:
                        sale_report = sale_order_id.partner_id.sale_report_model_id
                    # elif sale_rep:
                    #     sale_report = sale_rep
                    else:
                        sale_report = self.env.ref('sale.action_report_saleorder', raise_if_not_found=True)

                sale_pdf, _ = sale_report._render_qweb_pdf(sale_order_id.id)
                if sale_pdf:
                    pdfs.append(sale_pdf)
                if sale_order_id.fsm_task_ids:
                    intervention_report = self.env.ref('sale_fsm_extend.project_task_report_id', raise_if_not_found=True)
                    if intervention_report:
                        tasks_pdf, _ = intervention_report._render_qweb_pdf(sale_order_id.fsm_task_ids.ids)
                        if tasks_pdf:
                            pdfs.append(tasks_pdf)

        if self.attachment_ids:
            for a in self.attachment_ids:
                if a.name.split('.')[1] in ['pdf','PDF']:
                    name_invoice = self.name.replace('/', '_')
                    if name_invoice not in a.name:
                        try:
                            reader = PdfFileReader(io.BytesIO(base64.b64decode(a.datas)), strict=False,
                                                   overwriteWarnings=False)
                        except Exception:
                            continue

                        writer = PdfFileWriter()
                        for page_number in range(0, reader.getNumPages()):
                            page = reader.getPage(page_number)
                            writer.addPage(page)

                        _buffer = io.BytesIO()
                        writer.write(_buffer)
                        my_pdf = _buffer.getvalue()
                        pdfs.append(my_pdf)

            if any(a.name.split('.')[1] in ['JPG', 'JPEG', 'PNG', 'png', 'jpg', 'jpeg'] for a in
                   self.attachment_ids):
                for a in self.attachment_ids.filtered(
                        lambda u: u.name.split('.')[1] in ['JPG', 'JPEG', 'PNG', 'png', 'jpg', 'jpeg']):
                    try:
                        image_reader = ImageReader(io.BytesIO(base64.b64decode(a.datas)))
                        writer = PdfFileWriter()

                    except:
                        continue

                    packet = io.BytesIO()
                    can = canvas.Canvas(packet)
                    can.drawImage(image_reader, x=160, y=280, width=300, height=300)
                    can.save()
                    can.showPage()
                    packet.seek(0)
                    _pdf = PdfFileReader(packet, overwriteWarnings=False)
                    writer.addPage(_pdf.getPage(0))
                    writer.write(packet)
                    img_pdf = packet.getvalue()
                    pdfs.append(img_pdf)


        mg = pdf.merge_pdf(pdfs)
        self.custom_report_file = base64.b64encode(mg)




