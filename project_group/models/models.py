# -*- coding: utf-8 -*-
from odoo import models, fields, api





class ProjectProject(models.Model):
    _inherit = 'project.project'

    group_ids = fields.Many2many('project.group',
                                string='Groupes chantier')


class ProjectGroup(models.Model):
    _name = 'project.group'
    _description = "Groupes de chantier"

    name = fields.Char(string='Code' ,required=True)
    description = fields.Text(string='Description')
    # project_id = fields.Many2one('project.project', string='Projet')


class SaleOrder(models.Model):
    _inherit ='sale.order'

    group_chantier_id = fields.Many2one('project.group',domain="[('id','in',group_ids)]", string='Groupe Chantier', tracking=True)
    group_ids = fields.Many2many('project.group',compute='compute_group_ids', store=True)

    @api.depends('chantier_id','chantier_id.group_ids')
    def compute_group_ids(self):
        for record in self:
            if record.chantier_id:
                if record.chantier_id.group_ids:
                        record.group_ids = record.chantier_id.group_ids


class ProjectTask(models.Model):
    _inherit = 'project.task'

    group_chantier_id = fields.Many2one('project.group', related='fsm_sale_id.group_chantier_id', store=True)

