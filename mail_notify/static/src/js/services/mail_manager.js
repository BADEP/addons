odoo.define('mail_notify.chat_manager', function (require) {
"use strict";
var core = require('web.core');
var bus = require('bus.bus').bus;
var _t = core._t;
var ChatManager = require('mail.chat_manager');

var preview_msg_max_size = 350;

ChatManager.notify_incoming_message = function (msg, options) {
        if (bus.is_odoo_focused() && options.is_displayed) {
            // no need to notify
            return;
        }
        //Set icon to module icon by defaut
        if (Boolean(msg.module_icon)) {
            icon = msg.module_icon;
        }
        // for instant messaging the icon will be set to the user avatar
        if (msg.model == "mail.channel" && Boolean(msg.avatar_src)) {
            icon = msg.avatar_src;
        }
        var title = _t('New message');
        if (msg.author_id[1]) {
            title = _.escape(msg.author_id[1]);
        }
        if (msg.subject) {
            title = title + ": " + msg.subject;
        }
        else if (msg.model != "mail.channel" && msg.record_name) {
            title = title + ": " + msg.record_name;
        }
        var content = utils.parse_and_transform(msg.body, utils.strip_html).substr(0, preview_msg_max_size);

        if (!bus.is_odoo_focused()) {
            global_unread_counter++;
            var tab_title = _.str.sprintf(_t("%d Messages"), global_unread_counter);
            web_client.set_title_part("_chat", tab_title);
        }
        utils.send_notification(web_client, title, content, function ( ){window.open(msg.url);}, icon);
    }
return ChatManager;

});