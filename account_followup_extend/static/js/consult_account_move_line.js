odoo.define('account_followup_extend.FollowupFormController', function (require) {
"use strict";


        var rpc = require('web.rpc');
        var FollowupFormController = require('account_followup.FollowupFormController');
        FollowupFormController.include({

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------
    /**
     * @override
     */
   renderButtons: function () {
        this._super.apply(this, arguments);
        var self = this;
        this.$buttons.on('click', '.oe_consult_partner_account_move_line', function () {
                console.log('fffffff', self)
                return self._rpc({
                    model: 'res.partner',
                    method: 'consult_account_move_line',
                    args: [[]],
                }).then(function (results) {
                    var action = {
                        type: "ir.actions.act_window",
                        name: "Écritures comptables",
                        res_model: "account.move.line",
                        domain: [['partner_id', 'in', self.getSelectedIds()],['full_reconcile_id', '=', false], ['balance', '!=', 0], ['account_id.reconcile', '=', true], ['user_type_id', '=', results.user_type_id]],
                        views: [[results.view_id, "list"]],
                        target: 'current',
                                    };
                    self.do_action(action);
                          });
            });
    },
/*
    _OnclickV: function () {
         var self = this;
         rpc.query({
            model: 'res.partner',
            method: 'consult_account_move_line',
            args: [[]],
        }).then(function (res) {
             var action = {
                type: "ir.actions.act_window",
                name: "Écritures comptables",
                res_model: "account.move.line",
                domain: [['partner_id', 'in', this.getSelectedIds()],['full_reconcile_id', '=', false], ['balance', '!=', 0], ['account_id.reconcile', '=', true]],
                views: [[res.view_id, "list"]],
                target: 'current',
            };
            self.do_action(action);
        });
    },
*/
});
});