/**
 * Create and register Controller for new button
 */
 odoo.define('add_button_to_tree_view.SaleOrderButtonListView', function (require) {
"use strict";

var ListView = require('web.ListView');
var SaleOrderButtonListController = require('add_button_to_tree_view.SaleOrderButtonListController');
var viewRegistry = require('web.view_registry');


var SaleOrderButtonListView = ListView.extend({
    config: _.extend({}, ListView.prototype.config, {
        Controller: SaleOrderButtonListController,
    }),
});

viewRegistry.add('sale_order_tree_view_button', SaleOrderButtonListView);

return SaleOrderButtonListView;

});