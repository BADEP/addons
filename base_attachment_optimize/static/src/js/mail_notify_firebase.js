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
        messaging.usePublicVapidKey(result.fcm_vapid_key);
        messaging.onMessage(function(data) {
            navigator.serviceWorker.ready.then(function(registration) {
                //console.log('New message: ', data.notification);
                registration.showNotification(data.notification.title, {
                    body: data.notification.body,
                    icon: data.notification.icon,
                    click_action: data.notification.click_action,
                    time_to_live: data.notification.time_to_live,
                    data: data.notification.data,
                    tag: data.notification.tag
                });
            });
        });

        messaging.getToken().then((currentToken) => {
            if (currentToken) {
                //console.log(currentToken);
                sendTokenToServer(currentToken);
            }
        }).catch((err) => {
            console.log('An error occurred while retrieving token. ', err);
        });

        messaging.onTokenRefresh(() => {
            messaging.getToken().then((refreshedToken) => {
                //console.log(refreshedToken);
                setTokenSentToServer(false);
                sendTokenToServer(refreshedToken);
            }).catch((err) => {
                console.log('Unable to retrieve refreshed token ', err);
            });
        });

        function sendTokenToServer(currentToken) {
            if (!isTokenSentToServer()) {
                //console.log('Sending token to server...');
                document.cookie = "token=" + currentToken;
                location.reload();
                setTokenSentToServer(true);
            }
        }
        function isTokenSentToServer() {
            return window.localStorage.getItem('sentToServer') === '1';
        }
        function setTokenSentToServer(sent) {
            window.localStorage.setItem('sentToServer', sent ? '1' : '0');
        }
    }
});
});
