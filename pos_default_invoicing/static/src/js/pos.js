odoo.define('pos_default_invoicing', function (require) {
"use strict";

var models = require('point_of_sale.models');
var chrome = require('point_of_sale.chrome');
var screens = require('point_of_sale.screens');

    var _super_order = models.Order.prototype;
    models.Order = models.Order.extend({
        initialize: function(attributes,options){
            var result = _super_order.initialize.apply(this,arguments);
            if(this.pos.config.pos_defaut_invoice){
                this.to_invoice     = true;
            }
            return result;
            
        },
    });
    
});

