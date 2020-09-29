odoo.define('mail_notify.BusService', function (require) {
"use strict";

var CrossTab = require('bus.CrossTab');
var core = require('web.core');
var ServicesMixin = require('web.ServicesMixin');
var BusService = require('bus.BusService')

BusService.include({
    sendNotification: function (title, content, callback, icon=false) {
        if (window.Notification && Notification.permission === "granted") {
            if (this.isMasterTab()) {
                try {
                    this._sendNativeNotification(title, content, callback, icon);
                } catch (error) {
                    if (error.message.indexOf('ServiceWorkerRegistration') > -1) {
                        this.do_notify(title, content);
                        this._beep();
                    } else {
                        throw error;
                    }
                }
            }
        } else {
            this.do_notify(title, content);
            if (this.isMasterTab()) {
                this._beep();
            }
        }
    },
    _sendNativeNotification: function (title, content, callback, icon=false) {
        if (!icon) {
            icon = "/mail/static/src/img/odoobot_transparent.png"
        }
        var notification = new Notification(
            _.unescape(title),
            {
                body: _.unescape(content),
                icon: icon
            });
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
        };
    },

});

return BusService;

});
