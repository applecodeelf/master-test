const metrics = document.querySelector("#metrics");
const services = document.querySelector("#services");
const logBox = document.querySelector("#log");
const refresh = document.querySelector("#refresh");

async function api(path, options = {}) {
  const res = await fetch(path, options);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

function metric(label, value) {
  return `<div class="metric"><strong>${value}</strong><span>${label}</span></div>`;
}

function addressUrl(item) {
  if (item.family === "inet6") return `http://[${item.address}]:7860`;
  return `http://${item.address}:7860`;
}

async function loadStatus() {
  const data = await api("/api/status");
  const addressLinks = (data.addresses || []).map(item => {
    const url = addressUrl(item);
    return `<a href="${url}" target="_blank">${item.scope}: ${url}</a>`;
  });
  if (data.tunnel_url) {
    addressLinks.unshift(`<a href="${data.tunnel_url}" target="_blank">public tunnel: ${data.tunnel_url}</a>`);
  }

  metrics.innerHTML = [
    metric("Battery", data.battery),
    metric("Storage free", data.storage_free),
    metric("Memory free", data.memory_free),
    metric("Uptime", data.uptime),
    metric("Host", data.host),
    `<div class="metric wide"><strong>Access URLs</strong><div class="links">${addressLinks.join("") || "No address detected"}</div></div>`,
  ].join("");
}

async function loadServices() {
  const data = await api("/api/services");
  services.innerHTML = data.services.map(service => `
    <article class="service">
      <h3>
        ${service.name}
        <span class="badge ${service.running ? "running" : "stopped"}">
          ${service.running ? "running" : "stopped"}
        </span>
      </h3>
      <div class="meta">${service.description}</div>
      <div class="meta">Port: ${service.port || "-"}</div>
      <div class="meta">PID: ${service.pid || "-"}</div>
      <div class="actions">
        <button class="primary" onclick="startService('${service.id}')">Start</button>
        <button class="danger" onclick="stopService('${service.id}')">Stop</button>
        <button onclick="showLog('${service.id}')">Log</button>
      </div>
    </article>
  `).join("");
}

async function startService(id) {
  await api(`/api/services/${id}/start`, { method: "POST" });
  await loadAll();
  await showLog(id);
}

async function stopService(id) {
  await api(`/api/services/${id}/stop`, { method: "POST" });
  await loadAll();
}

async function showLog(id) {
  const data = await api(`/api/services/${id}/log`);
  logBox.textContent = data.log || "No log output yet.";
}

async function loadAll() {
  try {
    await Promise.all([loadStatus(), loadServices()]);
  } catch (error) {
    logBox.textContent = String(error);
  }
}

refresh.addEventListener("click", loadAll);
loadAll();
setInterval(loadAll, 5000);
