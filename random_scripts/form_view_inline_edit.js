odoo.define('my_module.form_edit_inline', function (require) {
"use strict";

var FormView = require('web.FormView');

/**
 * This script allows landing of a Form View directly in Edit mode
 * and displays "Save" and "Cancel" buttons.
 * Native Odoo 'target' = 'inline' lands Form View in Edit mode but
 * it does not display any buttons.
 *
 * Usage: add 'target': 'in_line_edit' when calling ir.actions.act_window
 *
 */

FormView.include({
    /**
     * @override
     */
    _extractParamsFromAction: function (action) {
        var params = this._super.apply(this, arguments);
        if(action.target === 'in_line_edit') {
            params.mode = 'edit';
        }
        return params;
    },
});

});