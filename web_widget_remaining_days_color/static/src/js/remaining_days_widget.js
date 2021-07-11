odoo.define('web_widget_remaining_days_color.basic_fields', function (require) {
    "use strict";
    var session = require('web.session');
    const RemainingDays = require('web.basic_fields').RemainingDays;

    RemainingDays.include({
        _render: function () {
            this._super();
            const nowUTC = moment().utc();
            const nowUserTZ = nowUTC.clone().add(session.getTZOffset(nowUTC), 'minutes');
            const valueUserTZ = this.value.clone().add(session.getTZOffset(this.value), 'minutes');
            const diffDays = valueUserTZ.startOf('day').diff(nowUserTZ.startOf('day'), 'days');
            this.$el.toggleClass('text-success', diffDays > 0);
        }
    });

    return {
        RemainingDays: RemainingDays,
    };

});
