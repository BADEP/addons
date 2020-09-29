odoo.define('mail_notify.utils', function (require) {
"use strict";

//var CrossTab = require('bus.CrossTab');
//var core = require('web.core');
//var ServicesMixin = require('web.ServicesMixin');
var bus = require('bus.bus').bus
var MailUutils = require('mail.utils')
MailUutils.send_notification = function send_notification(widget, title, content, callback, icon=false) {
        if (window.Notification && Notification.permission === "granted") {
            if (bus.is_master) {
                _send_native_notification(title, content, callback, icon);
            }
        } else {
            widget.do_notify(title, content);
            if (bus.is_master) {
                _beep(widget);
            }
        }
    }
function _send_native_notification(title, content, callback, icon=false) {
        if (!icon) {
            icon = "/mail/static/src/img/odoo_o.png"
        }
        var notification = new Notification(title, {body: content, icon: icon});
        notification.onclick = function () {
            window.focus();
            if (this.cancel) {
                this.cancel();
            } else if (this.close) {
                this.close();
            }
            if (callback) {
                callback();
            }
        }
    }

return MailUutils;

});
