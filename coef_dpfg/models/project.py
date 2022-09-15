from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = 'project.project'

    coef = fields.Float(string='Coefficient', required=True)


class ProjectWbs(models.Model):
    _inherit = 'project.wbs'

    coef = fields.Float(string='Coefficient')

    @api.model
    def create(self, vals):
        if vals.get('project_id', False):
            wbs = self.env['project.project'].browse(vals['project_id'])
            if wbs and wbs.coef:
                vals['coef'] = wbs.coef
        return super(ProjectWbs, self).create(vals)

    @api.onchange('unit_price')
    def onchange_unit_price(self):
        for rec in self:
            rec.coef = rec.unit_price / sum(l.unit_cost * l.qty for l in rec.cost_line_ids)

    def write(self, vals):
        res = super(ProjectWbs, self).write(vals)
        for rec in self:
            if vals.get('coef', False):
                rec.unit_price = rec.coef * sum(l.unit_cost * l.qty for l in rec.cost_line_ids)
        return res


class SDP(models.Model):
    _inherit = 'wbs.cost.line'

    def write(self, vals):
        res = super(SDP, self).write(vals)
        if 'unit_cost' in vals or 'qty' in vals:
            self.wbs_id.unit_price = self.wbs_id.coef * sum(l.unit_cost * l.qty for l in self.wbs_id.cost_line_ids)
        return res

    @api.model
    def create(self, vals):
        res = super(SDP, self).create(vals)
        if res.wbs_id:
            res.wbs_id.unit_price = res.wbs_id.coef * sum(l.unit_cost * l.qty for l in res.wbs_id.cost_line_ids)
        return res
