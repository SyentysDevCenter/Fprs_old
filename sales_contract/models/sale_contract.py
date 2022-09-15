# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class SaleContract(models.Model):
    _name = 'sale.contract'
    _inherit = ["mail.thread"]
    _order = 'date_end desc'

    name = fields.Char('Numéro', default='/', required=True)
    customer_id = fields.Many2one('res.partner', 'Client', required=True)
    date_start = fields.Date('Date début')
    date_end = fields.Date('Date fin')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)
    pricelist_id = fields.Many2one('product.pricelist', 'Liste de prix')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company.id)
    commentaire = fields.Text('Commentaire')
    contract_actif = fields.Boolean(compute='compute_contact_actif')
    line_ids = fields.One2many('sale.contract.line', 'contract_id', 'Détail', copy=True)
    state = fields.Selection([('draft', 'Nouveau'), ('confirm', 'Validé')], default='draft')

    customer_ids = fields.Many2many('res.partner', string='Autre clients')

    chantier_id = fields.Many2one('project.project', string='Chantier')

    _sql_constraints = [(
        'unique_contract_chantier',
        'UNIQUE(chantier_id)',
        "Un seul contrat est permis pour un chantier."
    )]

    def unlink(self):
        if any(c.state != 'draft' for c in self):
            raise ValidationError("Vous ne pouvez pas supprimer des contrats validés")
        res = super().unlink()
        return res

    def set_contract_to_draft(self):
        for rec in self:
            rec.pricelist_id.active = False
            rec.pricelist_id = False
            if rec.chantier_id :
                rec.chantier_id.product_pricelist_id = False
            rec.state = 'draft'

    @api.model
    def create(self, vals):
        if not vals.get('name', False) or vals['name'] == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.contract')
        return super(SaleContract, self).create(vals)

    def compute_contact_actif(self):
        for rec in self:
            rec.contract_actif = rec.date_start and rec.date_start <=fields.Date.context_today(self) and\
                                 (not rec.date_end or rec.date_end > fields.Date.context_today(self))

    def Validate_contract(self):
        for rec in self:
            if not rec.date_end or rec.date_end >= fields.Date.context_today(self):
                new_pricelist = self.env['product.pricelist'].create(
                    {'name': 'Liste de prix du ' + str(rec.name) + 'client ' + str(rec.customer_id.name)})

                for line in rec.line_ids:
                    if line.type == 'price':
                        self.env['product.pricelist.item'].create({
                            'applied_on': '1_product',
                            'product_tmpl_id': line.product_id.id,
                            'date_start': rec.date_start or False,
                            'date_end': rec.date_end or False,
                            'compute_price': 'fixed',
                            'fixed_price': line.price,
                            'pricelist_id': new_pricelist.id

                        })
                    elif line.type == "discount":
                        self.env['product.pricelist.item'].create({
                            'applied_on': '1_product',
                            'product_tmpl_id': line.product_id.id,

                            'date_start': rec.date_start or False,
                            'date_end': rec.date_end or False,
                            'compute_price': 'percentage',
                            'percent_price': line.discount,
                            'pricelist_id': new_pricelist.id

                        })
                    if line.product_uom_id:
                        if line.product_id and line.product_id.product_variant_id and not line.product_id.product_variant_id.stock_move_ids:
                            line.product_id.write({'uom_id': line.product_uom_id.id,
                                                   'uom_po_id': line.product_uom_id.id,})
                if rec.chantier_id:
                    rec.chantier_id.product_pricelist_id = new_pricelist.id
                rec.customer_id.property_product_pricelist = new_pricelist.id

                if rec.customer_ids:
                    for c in rec.customer_ids:
                        c.property_product_pricelist = new_pricelist.id

                rec.pricelist_id = new_pricelist.id


                rec.state = 'confirm'

    def actualisation(self):
        return {
            'name': _("Actualiser les prix"),
            'type': 'ir.actions.act_window',
            'res_model': 'actualisation.prix.contrat',
            'view_mode': 'form',
            'view_id': self.env.ref('sales_contract.view_actualise_prix_form').id,
            'target': 'new',
            'context': {'default_sale_contrat_id': self.id}
        }

class SaleContractLine(models.Model):
    _name = 'sale.contract.line'

    product_id = fields.Many2one('product.template', "Article", required=True)
    type = fields.Selection([('price', 'Prix'), ('discount', 'Remise')], default='discount')
    price = fields.Float('Prix')
    discount = fields.Float('Remise')
    contract_id = fields.Many2one('sale.contract', 'Contrat', ondelete='cascade')
    product_uom_id = fields.Many2one('uom.uom', 'Udm')

    @api.onchange('product_id')
    def onchnage_product(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id
