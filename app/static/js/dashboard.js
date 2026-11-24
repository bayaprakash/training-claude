(function () {
  function formatBytes(n) {
    if (n == null || Number.isNaN(n)) return "—";
    const units = ["B", "KB", "MB", "GB", "TB"];
    let value = Number(n);
    let i = 0;
    while (value >= 1024 && i < units.length - 1) {
      value /= 1024;
      i += 1;
    }
    return `${value.toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
  }

  function severityForPercent(value) {
    if (value == null || Number.isNaN(Number(value))) return null;
    const n = Number(value);
    if (n >= 85) return "crit";
    if (n >= 70) return "warn";
    return "good";
  }

  function applySeverity(dd, box, percent) {
    if (!dd) return;
    dd.classList.remove("sev-good", "sev-warn", "sev-crit");
    if (box) box.classList.remove("sev-good-box", "sev-warn-box", "sev-crit-box");
    const sev = severityForPercent(percent);
    if (!sev) return;
    dd.classList.add(`sev-${sev}`);
    if (box) box.classList.add(`sev-${sev}-box`);
  }

  function setBadge(el, status) {
    if (!el) return;
    el.className = "badge status-badge";
    if (status === "online") {
      el.classList.add("badge-online");
      el.textContent = "online";
    } else if (status === "mock") {
      el.classList.add("badge-mock");
      el.textContent = "mock";
    } else if (status === "unreachable") {
      el.classList.add("badge-unreachable");
      el.textContent = "unreachable";
    } else {
      el.classList.add("badge-pending");
      el.textContent = status || "unknown";
    }
  }

  function setCardStatus(card, status) {
    card.classList.remove("is-online", "is-mock", "is-unreachable", "is-pending");
    if (status === "online") card.classList.add("is-online");
    else if (status === "mock") card.classList.add("is-mock");
    else if (status === "unreachable") card.classList.add("is-unreachable");
    else card.classList.add("is-pending");
  }

  function fillCard(card, metrics) {
    setBadge(card.querySelector(".status-badge"), metrics.status);
    setCardStatus(card, metrics.status);

    const cpu = card.querySelector(".cpu");
    const mem = card.querySelector(".mem");
    const net = card.querySelector(".net");
    const ports = card.querySelector(".ports");
    const collected = card.querySelector(".collected");
    const portsList = card.querySelector(".ports-list");
    const cpuBox = cpu ? cpu.closest("div") : null;
    const memBox = mem ? mem.closest("div") : null;

    if (cpu) {
      const pct = metrics.cpu ? metrics.cpu.percent : null;
      cpu.textContent = pct != null ? `${pct}%` : "—";
      applySeverity(cpu, cpuBox, pct);
    }
    if (mem) {
      if (metrics.memory && metrics.memory.percent != null) {
        mem.textContent = `${metrics.memory.percent}% (${formatBytes(metrics.memory.used)} / ${formatBytes(metrics.memory.free)} free)`;
        applySeverity(mem, memBox, metrics.memory.percent);
      } else {
        mem.textContent = "—";
        applySeverity(mem, memBox, null);
      }
    }
    if (net && metrics.network) {
      net.textContent = `${formatBytes(metrics.network.bytes_recv)} / ${formatBytes(metrics.network.bytes_sent)}`;
    }
    if (ports) {
      ports.textContent = Array.isArray(metrics.ports) ? String(metrics.ports.length) : "—";
    }
    if (portsList) {
      portsList.innerHTML = "";
      if (!metrics.ports || !metrics.ports.length) {
        const li = document.createElement("li");
        li.textContent = "No listening ports reported";
        portsList.appendChild(li);
      } else {
        metrics.ports.forEach((p) => {
          const li = document.createElement("li");
          li.textContent = `${p.address || "*:" + p.port} (${p.state || "LISTEN"})`;
          portsList.appendChild(li);
        });
      }
    }
    if (collected) {
      collected.textContent = metrics.collected_at
        ? `Collected at ${metrics.collected_at}`
        : "";
    }
  }

  async function refreshGrid() {
    const grid = document.getElementById("metrics-grid");
    if (!grid) return;
    const response = await fetch("/api/metrics", { headers: { Accept: "application/json" } });
    if (!response.ok) return;
    const data = await response.json();
    const byId = {};
    (data.servers || []).forEach((m) => {
      byId[m.server_id] = m;
    });
    grid.querySelectorAll("[data-server-id]").forEach((card) => {
      const metrics = byId[card.dataset.serverId];
      if (metrics) fillCard(card, metrics);
    });
  }

  async function refreshDetail() {
    const card = document.getElementById("detail-card");
    if (!card) return;
    const response = await fetch(`/api/metrics/${card.dataset.serverId}`, {
      headers: { Accept: "application/json" },
    });
    if (!response.ok) return;
    fillCard(card, await response.json());
  }

  async function refreshAll() {
    await Promise.all([refreshGrid(), refreshDetail()]);
    resetCountdown();
  }

  const source =
    document.getElementById("metrics-grid") || document.getElementById("detail-card");
  const seconds = source ? Math.max(5, Number(source.dataset.refresh || 30)) : 30;
  const hint = document.getElementById("refresh-hint");
  let remaining = seconds;

  function resetCountdown() {
    remaining = seconds;
    if (hint) hint.textContent = `Next auto-refresh in ${remaining}s`;
  }

  function tickCountdown() {
    remaining -= 1;
    if (remaining <= 0) remaining = seconds;
    if (hint) hint.textContent = `Next auto-refresh in ${remaining}s`;
  }

  const refreshBtn = document.getElementById("refresh-btn");
  if (refreshBtn) refreshBtn.addEventListener("click", () => refreshAll());

  refreshAll();
  setInterval(refreshAll, seconds * 1000);
  setInterval(tickCountdown, 1000);
})();
