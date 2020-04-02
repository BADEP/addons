odoo.define('mail_notify.BusService', function (require) {
    "use strict";
    var Session = require('web.Session');
    var ajax = require('web.ajax');
    console.log('Android: session declaration');
    Session.include({
        get_file: function(options) {
            if (typeof Android != "undefined") {Android.getFile(options);}
            if (this.override_session) {
                options.data.session_id = this.session_id;
            }
            options.session = this;
            return ajax.get_file(options);
        }
    });
    return Session;
    console.log('Android: return session');
});
