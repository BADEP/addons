odoo.define('mail_notify.Manager', function (require) {
"use strict";
var config = require('web.config');
var core = require('web.core');
var mailUtils = require('mail.utils');
var _t = core._t;
var MailManager = require('mail.Manager');

var PREVIEW_MSG_MAX_SIZE = 350;


MailManager.include({
    _addNewMessagePostprocessThread: function (message, options) {
        var self = this;
        _.each(message.getThreadIDs(), function (threadID) {
            var thread = self.getThread(threadID);
            if (thread) {
                if (
                    thread.getType() !== 'mailbox' &&
                    !message.isMyselfAuthor() &&
                    !message.isSystemNotification()
                ) {
                    if (thread.isTwoUserThread() && options.showNotification) {
                        if (
                            !self._isDiscussOpen() &&
                            !config.device.isMobile &&
                            !thread.isDetached()
                        ) {
                            // automatically open thread window
                            // while keeping it unread
                            thread.detach({ passively: true });
                        }
                        var query = { isVisible: false };
                        self._mailBus.trigger('is_thread_bottom_visible', thread, query);
                    }
                    if (options.showNotification) {
                        if (!self.call('bus_service', 'isOdooFocused')) {
                            self._notifyIncomingMessage(message);
                        }
                    }
                }
            }
        });
    },

   _notifyIncomingMessage: function (message) {
        if (this.call('bus_service', 'isOdooFocused')) {
            // no need to notify
            return;
        }
        var title = _t("New message");
        if (message.hasAuthor()) {
            title = _.escape(message.getAuthorName());
        }
        var content = mailUtils.parseAndTransform(message.getBody(), mailUtils.stripHTML)
            .substr(0, PREVIEW_MSG_MAX_SIZE);

        if (!this.call('bus_service', 'isOdooFocused')) {
            this._outOfFocusUnreadMessageCounter++;
            var tabTitle = _.str.sprintf(
                _t("%d Messages"),
                this._outOfFocusUnreadMessageCounter
            );
            this.trigger_up('set_title_part', {
                part: '_chat',
                title: tabTitle
            });
        }
        this.call('bus_service', 'sendNotification', title, content, function ( ){window.open(message.getURL());});
    },
});
return MailManager;

});