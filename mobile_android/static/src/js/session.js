odoo.define('mail_notify.BusService', function (require) {
    "use strict";
    var Session = require('web.Session');
    console.log('Android: session declaration');
    Session.include({
        get_file: function(options) {
            if (typeof Android != "undefined") {Android.getFile(options);}
            return ajax.get_file(options);
        }
    });
    return Session;
    console.log('Android: return session');
});
