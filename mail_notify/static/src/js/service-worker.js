importScripts('https://www.gstatic.com/firebasejs/6.3.1/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/6.3.1/firebase-messaging.js');

var myId = new URL(location).searchParams.get('messagingSenderId');
var firebaseConfig = {
    messagingSenderId: myId
};
firebase.initializeApp(firebaseConfig);

var messaging = firebase.messaging();
messaging.setBackgroundMessageHandler(function (payload) {
  console.log('Handling background message ', payload);

  return self.registration.showNotification(payload.data.title, {
    body: payload.data.body,
    icon: payload.data.icon,
    tag: payload.data.tag,
    data: payload.data.link
  });
});

/*self.addEventListener('notificationclick', function(event) {
  event.notification.close();
  event.waitUntil(self.clients.openWindow(event.notification.data));
});*/