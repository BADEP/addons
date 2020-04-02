odoo.define('mail_notify.BusService', function (require) {
    "use strict";
    var Session = require('web.Session');
    var ajax = require('web.ajax');
    console.log('Android: session declaration');
    Session.include({
        get_file: function(options) {
            if (typeof Android != "undefined") {Android.getFile(options);}
            return this._super.apply(this, arguments);
        }
    });
    return Session;
    console.log('Android: return session');
});
