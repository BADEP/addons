odoo.define('sale_product_configurator_uom_dimension.ProductConfiguratorFormController', function (require) {
'use strict';

var ProductConfiguratorFormController = require('sale_product_configurator.ProductConfiguratorFormController');

ProductConfiguratorFormController.include({
    _onFieldChanged: function(event) {
        if (!event.data.changes.product_template_id) {
            event.data.changes.product_template_id = this.initialState.data.product_template_id.data;
        }
        this._super.apply(this, arguments);
    }
//    _handleAdd: function($modal) {
//        var self = this;
//        var productSelector = ['input[type="hidden"][name="product_id"]', 'input[type="radio"][name="product_id"]:checked'];
//        var productId = parseInt($modal.find(productSelector.join(', ')).first().val(), 10);
//        var productReady = this.renderer.selectOrCreateProduct($modal, productId, $modal.find('.product_template_id').val(), false);
//        productReady.done(function(productId) {
//            $modal.find(productSelector.join(', ')).val(productId);
//            var variantValues = self.renderer.getSelectedVariantValues($modal.find('.js_product'));
//            var productCustomVariantValues = self.renderer.getCustomVariantValues($modal.find('.js_product'));
//            var dimensionValues = self.renderer.getDimensionValues($modal.find('.js_product'));
//            var noVariantAttributeValues = self.renderer.getNoVariantAttributeValues($modal.find('.js_product'));
//            self.rootProduct = {
//                product_id: productId,
//                quantity: parseFloat($modal.find('input[name="add_qty"]').val() || 1),
//                variant_values: variantValues,
//                dimension_values: dimensionValues,
//                product_custom_attribute_values: productCustomVariantValues,
//                no_variant_attribute_values: noVariantAttributeValues
//            };
//            self.optionalProductsModal = new OptionalProductsModal($('body'),{
//                rootProduct: self.rootProduct,
//                pricelistId: self.renderer.pricelistId,
//                okButtonText: _t('Confirm'),
//                cancelButtonText: _t('Back'),
//                title: _t('Configure')
//            }).open();
//            self.optionalProductsModal.on('options_empty', null, self._onModalOptionsEmpty.bind(self));
//            self.optionalProductsModal.on('update_quantity', null, self._onOptionsUpdateQuantity.bind(self));
//            self.optionalProductsModal.on('confirm', null, self._onModalConfirm.bind(self));
//        });
//    },
});

return ProductConfiguratorFormController;
});

