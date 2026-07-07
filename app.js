const state = {
  data: null,
  locale: localStorage.getItem("strategyDashboardLocale") || "zh",
  window: "",
  strategyKey: "",
};

const i18n = {
  zh: {
    brandTitle: "ETF 策略研究展示",
    brandSub: "Interactive Strategy Case Study",
    navCompare: "策略对比",
    navExplorer: "回测探索",
    navExecution: "执行研究",
    navEngineering: "工程证据",
    heroKicker: "公开简历项目 · 研究边界清晰",
    heroTitle: "从 ETF 轮动假设到模拟执行链路的完整量化研究系统",
    heroLede: "B17 将特征工程、滚动回测、换手约束、模拟盘跟踪、5 分钟卖出执行研究和公开展示链路串成一个可验证项目。",
    heroCta: "查看策略证据",
    heroCta2: "查看安全边界",
    statusLabel: "当前状态",
    signalDay: "信号日",
    nextExec: "执行日",
    heroBoundary: "展示页只使用公开安全摘要，不包含账户、token 或真实下单能力。",
    guardrailResearch: "Research / Paper Only",
    guardrailResearchText: "研究与模拟跟踪，不是投资建议。",
    guardrailHypothesisText: "卖出延迟窗口只是冻结候选假设。",
    guardrailProdText: "没有任何 5m 卖出规则接入生产策略。",
    compareKicker: "Same-period backtest",
    compareTitle: "相同区间下的策略对比",
    compareText: "用同一信号日窗口比较 B17 base、Hold Bonus 和 Core2/Satellite，避免只挑单条曲线讲故事。",
    windowLabel: "回测窗口",
    thStrategy: "策略",
    thReturn: "总收益",
    thDrawdown: "最大回撤",
    thWin: "胜率",
    thTurnover: "平均换手",
    thHold: "平均持有",
    explorerKicker: "Backtest explorer",
    explorerTitle: "交互式净值曲线",
    explorerText: "选择策略查看最近样本曲线。曲线来自 public-safe JSON 摘要，不读取本地账户或券商数据。",
    strategyLabel: "策略",
    curveUnit: "累计收益 %",
    executionKicker: "Execution research",
    executionTitle: "5 分钟执行研究：冻结候选，不上线规则",
    executionText: "历史 1 分钟数据仍 blocked；当前结论只来自 5m proxy。它支持“延迟卖出窗口”这个候选假设，但不允许直接接入交易。",
    hypothesisTitle: "候选窗口：sell_10m 到 sell_50m",
    hypothesisText: "代表候选是 sell_45m，约 A 股 10:15；它只是验证锚点，不是“10:15 卖出规则”。",
    sampleCoverage: "覆盖样本",
    validationNeed: "下一步验证",
    policyChartTitle: "固定时间策略表现",
    policyChartUnit: "相对开盘改善 %",
    engineeringKicker: "Engineering evidence",
    engineeringTitle: "从研究到展示的工程链路",
    engineeringText: "展示系统强调可复现 artifact、刷新状态、公开安全数据和明确的执行边界。",
    footerText: "公开安全的项目展示页。非投资建议。",
    totalReturn: "总收益",
    maxDrawdown: "最大回撤",
    winRate: "胜率",
    meanTurnover: "平均换手",
    avgHolding: "平均持有",
    days: "天",
    warning: "警告",
  },
  en: {
    brandTitle: "ETF Strategy Research",
    brandSub: "Interactive Strategy Case Study",
    navCompare: "Comparison",
    navExplorer: "Backtest",
    navExecution: "Execution",
    navEngineering: "Engineering",
    heroKicker: "Resume-ready case study · explicit research boundaries",
    heroTitle: "A full quant research system from ETF rotation hypothesis to simulated execution",
    heroLede: "B17 connects feature engineering, walk-forward tests, turnover constraints, simulated tracking, 5-minute execution research, and public deployment into one verifiable project.",
    heroCta: "Explore evidence",
    heroCta2: "Read guardrails",
    statusLabel: "Current status",
    signalDay: "Signal day",
    nextExec: "Execution day",
    heroBoundary: "This page uses public-safe summaries only. It includes no account data, tokens, or live order capability.",
    guardrailResearch: "Research / Paper Only",
    guardrailResearchText: "Research and simulated tracking, not investment advice.",
    guardrailHypothesisText: "The delayed-sell window is only a frozen candidate hypothesis.",
    guardrailProdText: "No 5m sell rule is connected to production strategy logic.",
    compareKicker: "Same-period backtest",
    compareTitle: "Strategy comparison on matched windows",
    compareText: "B17 base, Hold Bonus, and Core2/Satellite are compared on the same signal-day windows to avoid cherry-picking a single curve.",
    windowLabel: "Backtest window",
    thStrategy: "Strategy",
    thReturn: "Total return",
    thDrawdown: "Max drawdown",
    thWin: "Win rate",
    thTurnover: "Mean turnover",
    thHold: "Avg holding",
    explorerKicker: "Backtest explorer",
    explorerTitle: "Interactive equity curve",
    explorerText: "Select a strategy to inspect the recent sample curve. The chart is generated from public-safe JSON, not broker or account data.",
    strategyLabel: "Strategy",
    curveUnit: "Cumulative return %",
    executionKicker: "Execution research",
    executionTitle: "5m execution research: frozen hypothesis, not a live rule",
    executionText: "Historical 1m data remains blocked. The current finding comes from a 5m proxy only. It supports a delayed-sell window hypothesis, not production execution.",
    hypothesisTitle: "Candidate window: sell_10m to sell_50m",
    hypothesisText: "The representative candidate is sell_45m, around 10:15 China A-share time. It is a validation anchor, not a 10:15 sell rule.",
    sampleCoverage: "Sample coverage",
    validationNeed: "Next validation",
    policyChartTitle: "Fixed-time policy results",
    policyChartUnit: "Improvement vs open %",
    engineeringKicker: "Engineering evidence",
    engineeringTitle: "Research-to-publication engineering chain",
    engineeringText: "The system emphasizes reproducible artifacts, refresh status, public-safe data, and explicit execution boundaries.",
    footerText: "Public-safe portfolio dashboard. Not investment advice.",
    totalReturn: "Total return",
    maxDrawdown: "Max drawdown",
    winRate: "Win rate",
    meanTurnover: "Mean turnover",
    avgHolding: "Avg holding",
    days: "days",
    warning: "Warning",
  },
};

const strategyNames = {
  b17_base_5d: "B17 Base 5D",
  "hold_bonus_1.0": "Hold Bonus",
  core2_satellite1: "Core2 / Satellite",
};

function t(key) {
  return i18n[state.locale][key] || key;
}

function fmtPct(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "--";
  const n = Number(value);
  const sign = n > 0 ? "+" : "";
  return `${sign}${n.toFixed(digits)}%`;
}

function fmtNum(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "--";
  return Number(value).toFixed(digits);
}

function applyLocale() {
  document.documentElement.lang = state.locale === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.getElementById("localeToggle").textContent = state.locale === "zh" ? "EN" : "中文";
}

function getRowsForWindow() {
  return state.data.same_period.summary.filter((row) => row.window === state.window);
}

function renderHero() {
  const refresh = state.data.refresh_status;
  const hb = state.data.live_signals["hold_bonus_1.0"];
  const core2 = state.data.live_signals.core2_satellite1;
  document.getElementById("refreshStatus").textContent = refresh.ok ? "OK" : t("warning");
  document.getElementById("signalDay").textContent = refresh.live_signal_source_day || hb.signal_source_day || "--";
  document.getElementById("nextExec").textContent = hb.next_exec_day || core2.next_exec_day || "--";
  document.getElementById("holdBonusTargets").textContent = hb.top_targets.map((x) => x.symbol).join(" / ") || "--";
  document.getElementById("core2Targets").textContent = core2.top_targets.map((x) => x.symbol).join(" / ") || "--";
  document.getElementById("generatedAt").textContent = `data: ${state.data.generated_at.slice(0, 19).replace("T", " ")} UTC`;
}

function renderWindowOptions() {
  const windows = [...new Set(state.data.same_period.summary.map((row) => row.window))].sort((a, b) => Number(a) - Number(b));
  state.window = state.window || windows[windows.length - 1] || "";
  const select = document.getElementById("windowSelect");
  select.innerHTML = windows.map((w) => `<option value="${w}">${w}D</option>`).join("");
  select.value = state.window;
}

function renderStrategyOptions() {
  const keys = Object.keys(state.data.same_period.curves).filter((key) => key.endsWith(`__${state.window}`));
  state.strategyKey = keys.includes(state.strategyKey) ? state.strategyKey : keys[0] || "";
  const select = document.getElementById("strategySelect");
  select.innerHTML = keys
    .map((key) => {
      const [strategy, window] = key.split("__");
      return `<option value="${key}">${strategyNames[strategy] || strategy} · ${window}D</option>`;
    })
    .join("");
  select.value = state.strategyKey;
}

function renderMetrics() {
  const rows = getRowsForWindow();
  const host = document.getElementById("metricCards");
  host.innerHTML = rows
    .map(
      (row) => `
        <article class="metric-card">
          <span>${strategyNames[row.strategy] || row.strategy}</span>
          <strong>${fmtPct(row.total_return_pct)}</strong>
          <dl>
            <div><dt>${t("maxDrawdown")}</dt><dd>${fmtPct(row.max_drawdown_pct)}</dd></div>
            <div><dt>${t("avgHolding")}</dt><dd>${fmtNum(row.avg_holding_days, 1)} ${t("days")}</dd></div>
          </dl>
        </article>
      `
    )
    .join("");
}

function renderTable() {
  const rows = getRowsForWindow();
  document.getElementById("comparisonTable").innerHTML = rows
    .map(
      (row) => `
        <tr>
          <td>${strategyNames[row.strategy] || row.strategy}</td>
          <td>${fmtPct(row.total_return_pct)}</td>
          <td>${fmtPct(row.max_drawdown_pct)}</td>
          <td>${fmtPct(row.win_rate_pct)}</td>
          <td>${fmtPct(row.mean_turnover_pct)}</td>
          <td>${fmtNum(row.avg_holding_days, 2)} ${t("days")}</td>
        </tr>
      `
    )
    .join("");
}

function lineChart(points) {
  const width = 820;
  const height = 280;
  const pad = { top: 20, right: 26, bottom: 34, left: 52 };
  if (!points || points.length < 2) return "<p>No data</p>";
  const values = points.map((p) => Number(p.value_pct));
  const min = Math.min(...values, 0);
  const max = Math.max(...values, 0);
  const span = max - min || 1;
  const x = (i) => pad.left + (i / (points.length - 1)) * (width - pad.left - pad.right);
  const y = (v) => pad.top + ((max - v) / span) * (height - pad.top - pad.bottom);
  const line = points.map((p, i) => `${i === 0 ? "M" : "L"}${x(i).toFixed(1)},${y(p.value_pct).toFixed(1)}`).join(" ");
  const area = `${line} L${x(points.length - 1)},${y(min)} L${x(0)},${y(min)} Z`;
  const ticks = [min, (min + max) / 2, max];
  return `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Equity curve">
      ${ticks
        .map(
          (tick) => `
            <line x1="${pad.left}" x2="${width - pad.right}" y1="${y(tick)}" y2="${y(tick)}" stroke="rgba(255,255,255,.08)" />
            <text class="axis-text" x="8" y="${y(tick) + 4}">${tick.toFixed(1)}%</text>
          `
        )
        .join("")}
      <path class="area-path" d="${area}" />
      <path class="line-path" d="${line}" />
      <text class="axis-text" x="${pad.left}" y="${height - 8}">${points[0].date}</text>
      <text class="axis-text" text-anchor="end" x="${width - pad.right}" y="${height - 8}">${points[points.length - 1].date}</text>
    </svg>
  `;
}

function barChart(rows) {
  const fixed = rows.filter((r) => /^sell_(open|\d+m)$/.test(r.policy || ""));
  const width = 820;
  const height = 300;
  const pad = { top: 18, right: 20, bottom: 62, left: 44 };
  const vals = fixed.map((r) => Number(r.median_vs_open_pct || 0));
  const min = Math.min(...vals, 0);
  const max = Math.max(...vals, 0.1);
  const span = max - min || 1;
  const innerW = width - pad.left - pad.right;
  const barW = innerW / fixed.length - 8;
  const y = (v) => pad.top + ((max - v) / span) * (height - pad.top - pad.bottom);
  const zeroY = y(0);
  return `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Policy bar chart">
      <line x1="${pad.left}" x2="${width - pad.right}" y1="${zeroY}" y2="${zeroY}" stroke="rgba(255,255,255,.18)" />
      ${fixed
        .map((row, i) => {
          const value = Number(row.median_vs_open_pct || 0);
          const x = pad.left + i * (innerW / fixed.length) + 4;
          const top = Math.min(y(value), zeroY);
          const h = Math.abs(zeroY - y(value));
          const fill = value >= 0 ? "url(#barGold)" : "#e47767";
          return `
            <rect x="${x}" y="${top}" width="${barW}" height="${Math.max(h, 2)}" rx="8" fill="${fill}" />
            <text class="bar-label" transform="translate(${x + barW / 2},${height - 32}) rotate(-35)" text-anchor="end">${row.policy.replace("sell_", "")}</text>
            <text class="bar-value" x="${x + barW / 2}" y="${top - 7}" text-anchor="middle">${value.toFixed(2)}</text>
          `;
        })
        .join("")}
      <defs>
        <linearGradient id="barGold" x1="0" x2="0" y1="0" y2="1">
          <stop stop-color="#f0d99b" />
          <stop offset="1" stop-color="#b48743" />
        </linearGradient>
      </defs>
    </svg>
  `;
}

function renderCurve() {
  const points = state.data.same_period.curves[state.strategyKey] || [];
  const [strategy, window] = state.strategyKey.split("__");
  document.getElementById("curveTitle").textContent = `${strategyNames[strategy] || strategy} · ${window || ""}D`;
  document.getElementById("curveChart").innerHTML = lineChart(points);
}

function renderExecution() {
  document.getElementById("policyChart").innerHTML = barChart(state.data.execution_research.fixed_time_policy_summary);
  document.getElementById("windowClusters").innerHTML = state.data.execution_research.window_clusters
    .map(
      (row) => `
        <article class="cluster-card">
          <strong>${row.window}</strong>
          <span>${row.policies}</span>
          <span>mean ${fmtPct(row.average_mean_vs_open_pct)} · median ${fmtPct(row.average_median_vs_open_pct)}</span>
          <span>win ${fmtPct(row.average_win_rate_pct)}</span>
        </article>
      `
    )
    .join("");
}

function renderTimeline() {
  document.getElementById("timeline").innerHTML = state.data.engineering_timeline
    .map(
      (item, index) => `
        <div class="timeline-item">
          <strong>${String(index + 1).padStart(2, "0")} · ${item.phase}</strong>
          <span>${item.label}</span>
        </div>
      `
    )
    .join("");
}

function renderAll() {
  applyLocale();
  renderHero();
  renderWindowOptions();
  renderStrategyOptions();
  renderMetrics();
  renderTable();
  renderCurve();
  renderExecution();
  renderTimeline();
}

async function boot() {
  const response = await fetch("./data/strategy_dashboard_data.json", { cache: "no-store" });
  state.data = await response.json();
  renderAll();

  document.getElementById("localeToggle").addEventListener("click", () => {
    state.locale = state.locale === "zh" ? "en" : "zh";
    localStorage.setItem("strategyDashboardLocale", state.locale);
    renderAll();
  });

  document.getElementById("windowSelect").addEventListener("change", (event) => {
    state.window = event.target.value;
    state.strategyKey = "";
    renderAll();
  });

  document.getElementById("strategySelect").addEventListener("change", (event) => {
    state.strategyKey = event.target.value;
    renderCurve();
  });
}

boot().catch((error) => {
  document.body.innerHTML = `<pre style="padding:24px;color:#f6efe1">Dashboard failed to load: ${error.message}</pre>`;
});
