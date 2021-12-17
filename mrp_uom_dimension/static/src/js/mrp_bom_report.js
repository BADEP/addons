odoo.define('mrp_uom_dimension.mrp_bom_report', function (require) {
"use strict";

var core = require('web.core');
var _t = core._t;

var MrpBomReport = require('mrp.mrp_bom_report');

MrpBomReport.include({
    renderSearch: function () {
        this._super.apply(this, arguments);
        this.$searchView.find('.o_mrp_bom_report_dimension').on('change', this._onChangeDimensions.bind(this)).change();
    },
    _onChangeDimensions: function (ev) {
        var dimensions = {};
        for (const element of this.$searchView.find('.o_mrp_bom_report_dimension')) {
            dimensions[parseInt(element.getAttribute("data-dimension_id"))] = parseFloat(element.value);
        }
        this.given_context.dimensions = dimensions;
        this._reload();
    }
});

});
