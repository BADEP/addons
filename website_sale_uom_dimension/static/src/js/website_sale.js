odoo.define('website_sale_uom_dimension.website_sale', function (require) {
"use strict";

var publicWidget = require('web.public.widget');
const wUtils = require('website.utils');

publicWidget.registry.WebsiteSale.include({
    _handleAdd: function ($form) {
        var self = this;
        this.$form = $form;

        var productSelector = [
            'input[type="hidden"][name="product_id"]',
            'input[type="radio"][name="product_id"]:checked'
        ];

        var productReady = this.selectOrCreateProduct(
            $form,
            parseInt($form.find(productSelector.join(', ')).first().val(), 10),
            $form.find('.product_template_id').val(),
            false
        );

        return productReady.then(function (productId) {
            $form.find(productSelector.join(', ')).val(productId);

            self.rootProduct = {
                product_id: productId,
                quantity: parseFloat($form.find('input[name="add_qty"]').val() || 1),
                product_custom_attribute_values: self.getCustomVariantValues($form.find('.js_product')),
                variant_values: self.getSelectedVariantValues($form.find('.js_product')),
                no_variant_attribute_values: self.getNoVariantAttributeValues($form.find('.js_product')),
                dimension_values: self.getDimensionValues($form.find('.js_product')),
            };
            return self._onProductReady();
        });
    },

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
    },

    _submitForm: function () {
        let params = this.rootProduct;
        params.add_qty = params.quantity;

        params.product_custom_attribute_values = JSON.stringify(params.product_custom_attribute_values);
        params.no_variant_attribute_values = JSON.stringify(params.no_variant_attribute_values);
        params.dimension_values = JSON.stringify(params.dimension_values);

        if (this.isBuyNow) {
            params.express = true;
        }

        return wUtils.sendRequest('/shop/cart/update', params);
    },
});
});
