/**
 * Sale Order List View Custom Button Handler
 */
 odoo.define('add_button_to_tree_view.SaleOrderButtonListController', function (require) {
"use strict";

var core = require('web.core');
var ListController = require('web.ListController');

var qweb = core.qweb;


var SaleOrderButtonListController = ListController.extend({

    // -------------------------------------------------------------------------
    // Public
    // -------------------------------------------------------------------------

    /**
     * @override
     */
    renderButtons: function ($node) {
        this._super.apply(this, arguments);
        var $buttonNext = $(qweb.render('SaleOrderButton.Buttons'));
        $buttonNext.on('click', this._onSaleOrderCustomButton.bind(this));
        $buttonNext.prependTo($node.find('.o_list_buttons'));
    },

    // -------------------------------------------------------------------------
    // Handlers
    // -------------------------------------------------------------------------

    /**
     * Handler called when the user clicks our Custom Button.
     * Here you can add any logic. For this module we called
     * sale.order python method thru rpc.
     */
    _onSaleOrderCustomButton: function () {            
        var self = this; 
        this._rpc({
                model: 'sale.order',
                method: 'js_sale_order_custom_button',
                args: [""], 
            }).then(function (result) {
                self.do_action(result);
        });            
    },
});

return SaleOrderButtonListController;

});