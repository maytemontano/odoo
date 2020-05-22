Add Custom Button to Tree View
------------------------------

This module adds a custom button to tree view and register its JS Controller
and action. It has been fully tested in Odoo v13.0.

js_class "sale_order_tree_view_button" has to be added to the tree node
                
        <xpath expr="//tree" position="attributes">
                <attribute name="js_class">sale_order_tree_view_button</attribute>
            </xpath>
        </field>
        