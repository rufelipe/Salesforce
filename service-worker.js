self.addEventListener("push", function (event) {
  let data = {};
  try { data = event.data ? event.data.json() : {}; } catch (error) {}
  const title = data.title || "Lembrete do YODA";
  const options = {
    body: data.body || "Você tem um compromisso em breve.",
    icon: "/yoda-icon.png",
    badge: "/yoda-icon.png",
    tag: data.tag || "yoda-reminder",
    renotify: true,
    data: { url: data.url || "/" }
  };
  event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener("notificationclick", function (event) {
  event.notification.close();
  const target = new URL(event.notification.data && event.notification.data.url || "/", self.location.origin).href;
  event.waitUntil((async function () {
    const clientsList = await clients.matchAll({ type: "window", includeUncontrolled: true });
    for (const client of clientsList) {
      if (client.url.startsWith(self.location.origin) && "focus" in client) {
        await client.focus();
        client.navigate(target);
        return;
      }
    }
    if (clients.openWindow) return clients.openWindow(target);
  })());
});
