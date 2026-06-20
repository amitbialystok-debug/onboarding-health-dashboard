// Frontend logic — fetches data from the API and renders the dashboard

const API_URL = "http://localhost:8000/api/v1/accounts";

function riskClass(riskLevel) {
  if (riskLevel === "Healthy")  return "healthy";
  if (riskLevel === "At Risk")  return "at-risk";
  if (riskLevel === "Critical") return "critical";
  return "";
}

function buildCard(account) {
  const { company_name, industry, health } = account;
  const { score, risk_level, signals } = health;
  const cls = riskClass(risk_level);

  const signalItems = signals
    .map(s => `<li>${s}</li>`)
    .join("");

  return `
    <article class="account-card ${cls}">
      <div class="card-header">
        <div>
          <div class="card-company">${company_name}</div>
          <div class="card-industry">${industry || "—"}</div>
        </div>
        <div class="card-score-block">
          <div class="card-score">${score}</div>
          <div class="card-score-label">/ 100</div>
        </div>
      </div>
      <span class="risk-badge ${cls}">${risk_level}</span>
      <div class="signals-label">Signals</div>
      <ul class="signals-list">${signalItems}</ul>
    </article>
  `;
}

function renderSummary(accounts) {
  const counts = { healthy: 0, "at-risk": 0, critical: 0 };
  for (const a of accounts) {
    const cls = riskClass(a.health.risk_level);
    if (cls in counts) counts[cls]++;
  }
  document.getElementById("count-total").textContent   = accounts.length;
  document.getElementById("count-healthy").textContent = counts["healthy"];
  document.getElementById("count-at-risk").textContent = counts["at-risk"];
  document.getElementById("count-critical").textContent = counts["critical"];
}

function showError(message) {
  const banner = document.getElementById("error-banner");
  banner.textContent = message;
  banner.classList.remove("hidden");
}

async function loadDashboard() {
  try {
    const response = await fetch(API_URL);
    if (!response.ok) {
      throw new Error(`API returned ${response.status} ${response.statusText}`);
    }
    const accounts = await response.json();

    renderSummary(accounts);

    const grid = document.getElementById("accounts-grid");
    if (accounts.length === 0) {
      grid.innerHTML = `<p style="color: var(--color-text-muted); grid-column: 1/-1;">No accounts found.</p>`;
      return;
    }
    grid.innerHTML = accounts.map(buildCard).join("");
  } catch (err) {
    showError(`Failed to load dashboard data: ${err.message}. Is the API server running?`);
  }
}

document.addEventListener("DOMContentLoaded", loadDashboard);
