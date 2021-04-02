odoo.define('mail_notify.Firebase', function (require) {
    "use strict";
    var rpc = require('web.rpc');
    var config = rpc.query({
        model: 'ir.config_parameter',
        method: 'get_fcm_config',
    }).then(function(result){
        if (result.is_fcm_enabled && firebase.messaging.isSupported()) {
            var firebaseConfig = {
                messagingSenderId: result.fcm_messaging_id
            };
            firebase.initializeApp(firebaseConfig);
            var messaging = firebase.messaging();
            messaging.usePublicVapidKey(result.fcm_vapid_key);
            messaging.getToken().then((currentToken) => {
                if (currentToken) {
                    if (result.debug_fcm) {
                        isTokenSentToServer() ? console.log('Existing token found: ', currentToken) : console.log('New token received: ', currentToken);
                    }
                    sendTokenToServer(currentToken);
                }
            }).catch((err) => {
                console.log('An error occurred while retrieving token. ', err);
            });
            messaging.onTokenRefresh(() => {
                messaging.getToken().then((refreshedToken) => {
                    setTokenSentToServer(false);
                    if (result.debug_fcm) {
                        console.log('New refreshed token received: ', refreshedToken);
                    }
                    sendTokenToServer(refreshedToken);
                }).catch((err) => {
                    console.log('Unable to retrieve refreshed token ', err);
                });
            });
            messaging.onMessage((payload) => {
                if (result.debug_fcm) {
                    console.log('Message received. ', payload);
                }
                if (result.foreground_notifications) {
                    var notificationTitle = payload.notification.title;
                    var notificationOptions = {
                        body: payload.notification.body,
                        icon: payload.notification.icon,
                        image: payload.notification.image
                    };
                    var notification = new Notification(notificationTitle, notificationOptions);
                }
            });

            function sendTokenToServer(currentToken) {
                if (!isTokenSentToServer()) {
                    rpc.query({
                        model:  'res.users.token',
                        method: 'add_token',
                        args: [currentToken]
                    });
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
