odoo.define('sale_uom_dimension.ProductConfiguratorFormRenderer', function (require) {
'use strict';

var concurrency = require('web.concurrency');
var core = require('web.core');
var utils = require('web.utils');
var ajax = require('web.ajax');
var _t = core._t;
var ProductConfiguratorFormRenderer = require('sale.ProductConfiguratorFormRenderer');

ProductConfiguratorFormRenderer.include({
    getDimensionValues: function($container){
        var dimensionValues = [];
        $container.find('.js_dimension').each(function() {
            var $dimensionValueInput = $(this);
            if ($dimensionValueInput.length !== 0) {
                dimensionValues.push({
                    'dimension_id': $dimensionValueInput.data('dimension_id'),
                    'quantity': $dimensionValueInput.val(),
                });
            }
        });
        return dimensionValues;
    }
});

return ProductConfiguratorFormRenderer;
});

