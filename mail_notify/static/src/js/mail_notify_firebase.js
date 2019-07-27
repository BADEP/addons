odoo.define('mail_notify.Firebase', function (require) {
"use strict";

var rpc = require('web.rpc');

var config = rpc.query({
    model: 'ir.config_parameter',
    method: 'get_fcm_config',
}).then(function(result){
    if (result.is_fcm_enabled) {
        var firebaseConfig = {
            messagingSenderId: result.fcm_messaging_id
        };
        firebase.initializeApp(firebaseConfig);
        var messaging = firebase.messaging();
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/mail_notify/static/src/js/service-worker.js').then(function(registration) {
                messaging.useServiceWorker(registration);
                messaging.usePublicVapidKey(result.fcm_vapid_key);

                messaging.onMessage(function(data) {
                    registration.showNotification(data.notification.title, {
                        body: data.notification.body,
                        icon: data.notification.icon,
                        click_action: data.notification.click_action,
                        time_to_live: data.notification.time_to_live,
                        data: data.notification.data,
                        tag: data.notification.tag
                    });
                });

                messaging.getToken().then((currentToken) => {
                    if (currentToken) {
                        rpc.query({
                            model:  'res.users.token',
                            method: 'add_token',
                            args: [currentToken]
                        });
                    }
                }).catch((err) => {
                    console.log('An error occurred while retrieving token. ', err);
                });

                messaging.onTokenRefresh(() => {
                    messaging.getToken().then((refreshedToken) => {
                        rpc.query({
                            model:  'res.users.token',
                            method: 'add_token',
                            args: [refreshedToken]
                        });
                    }).catch((err) => {
                        console.log('Unable to retrieve refreshed token ', err);
                    });
                });
            })
        }
    }
});
});