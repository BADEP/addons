odoo.define('mobile_android.Session', function (require) {
    "use strict";
    var Session = require('web.Session');
    var ajax = require('web.ajax');
    console.log('Android: session declaration');
    Session.include({
        get_file: function(options) {
            if (typeof Android != "undefined" && options.data.download) {Android.getFile(options.filename);}
            return this._super.apply(this, arguments);
        }
    });
    console.log('Android: return session');
    return Session;
});
