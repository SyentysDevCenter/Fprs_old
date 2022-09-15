odoo.define('partner_extend.view_amvl', function (require) {
"use strict";

var AbstractAction = require('web.AbstractAction');
var core = require('web.core');
var field_utils = require('web.field_utils');
var QWeb = core.qweb;


var ConsultAMVL = AbstractAction.extend({
    events: {
        "click .oe_consult_partner_account_move_line1": function () {return this._rpc({
                    model: 'res.partner',
                    method: 'consult_account_move_line',
                    args: [],
                });
         },
    },



});

core.action_registry.add('view_amvl', ConsultAMVL);

return ConsultAMVL;

});