(() => {
  const css = document.createElement("link");
  css.rel = "stylesheet";
  css.href = "./agent.css";
  document.head.appendChild(css);

  const escapeHtml = (value) =>
    String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");

  function createAgentSection() {
    if (document.getElementById("agent")) return;

    const nav = document.querySelector(".nav");
    if (nav) {
      const link = document.createElement("a");
      link.href = "#agent";
      link.textContent = "投研 Agent";
      nav.prepend(link);
    }

    const section = document.createElement("section");
    section.id = "agent";
    section.className = "section-shell agent-shell";
    section.innerHTML = `
      <div class="agent-heading">
        <div>
          <p class="section-kicker">Ascend-powered · Evidence-grounded</p>
          <h2>ETF Research Copilot · 投研证据 Agent</h2>
          <p>
            用自然语言提问，Agent 会先规划所需工具，再读取当前公开研究数据，最后通过昇腾 / AtomGit 模型生成带证据边界的回答。
          </p>
        </div>
        <div class="agent-status" id="agentStatus">
          <span class="agent-dot"></span>
          <div>
            <small>Ascend runtime</small>
            <strong>checking...</strong>
          </div>
        </div>
      </div>

      <div class="agent-grid">
        <div class="agent-chat-card">
          <div class="agent-quick-prompts" id="agentQuickPrompts">
            <button type="button" data-prompt="比较全样本三个策略的收益、最大回撤和换手率，哪个历史表现更强？">策略对比</button>
            <button type="button" data-prompt="当前研究信号快照是什么？数据是否有刷新警告？">信号快照</button>
            <button type="button" data-prompt="5分钟执行研究目前支持什么结论，哪些结论还不能下？">执行研究</button>
            <button type="button" data-prompt="从风险角度比较三个策略，并指出数据边界。">风险检查</button>
          </div>

          <div class="agent-messages" id="agentMessages" aria-live="polite">
            <article class="agent-message agent-message-assistant">
              <span>Agent</span>
              <p>你可以问策略对比、回撤、换手、模拟信号、5 分钟执行研究和数据风险。我不会连接券商，也不会生成真实订单。</p>
            </article>
          </div>

          <form class="agent-form" id="agentForm">
            <textarea id="agentQuestion" rows="3" maxlength="2000" placeholder="例如：比较 120 天窗口下三个策略，为什么不能只看收益率？" required></textarea>
            <button id="agentSubmit" type="submit">运行 Agent</button>
          </form>
        </div>

        <aside class="agent-trace-card">
          <div class="agent-panel-title">
            <span>Execution Trace</span>
            <strong id="agentLatency">--</strong>
          </div>
          <ol id="agentTrace" class="agent-trace">
            <li><span>01</span><div><strong>Plan</strong><small>等待问题</small></div></li>
            <li><span>02</span><div><strong>Retrieve</strong><small>仅读取公开安全研究数据</small></div></li>
            <li><span>03</span><div><strong>Synthesize</strong><small>昇腾模型生成证据化回答</small></div></li>
          </ol>
          <div class="agent-boundary">
            <strong>Hard Guardrails</strong>
            <p>Research-only · No broker · No live order · No personalized buy/sell instruction</p>
          </div>
          <details class="agent-evidence-details">
            <summary>查看最近一次工具证据</summary>
            <pre id="agentEvidence">No evidence yet.</pre>
          </details>
        </aside>
      </div>
    `;

    const guardrails = document.getElementById("guardrails");
    if (guardrails) guardrails.insertAdjacentElement("afterend", section);
    else document.querySelector("main")?.prepend(section);
  }

  function renderMessage(role, text) {
    const host = document.getElementById("agentMessages");
    const item = document.createElement("article");
    item.className = `agent-message agent-message-${role}`;
    item.innerHTML = `<span>${role === "user" ? "You" : "Agent"}</span><p>${escapeHtml(text).replaceAll("\n", "<br>")}</p>`;
    host.appendChild(item);
    host.scrollTop = host.scrollHeight;
  }

  async function checkHealth() {
    const status = document.querySelector("#agentStatus strong");
    const dot = document.querySelector("#agentStatus .agent-dot");
    try {
      const response = await fetch("/api/health", { cache: "no-store" });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      status.textContent = data.ascend_configured ? `${data.model} · ready` : `${data.model} · token required`;
      dot.classList.toggle("ok", Boolean(data.ascend_configured));
      dot.classList.toggle("warn", !data.ascend_configured);
    } catch (error) {
      status.textContent = "static preview · start FastAPI backend";
      dot.classList.add("warn");
    }
  }

  function renderTrace(data) {
    const trace = document.getElementById("agentTrace");
    if (Array.isArray(data.trace)) {
      trace.innerHTML = data.trace
        .map(
          (step, index) => `
            <li>
              <span>${String(index + 1).padStart(2, "0")}</span>
              <div>
                <strong>${escapeHtml(step.step)}</strong>
                <small>${escapeHtml(step.detail)}${step.fallback ? " · fallback router" : ""}</small>
              </div>
            </li>`
        )
        .join("");
    }
    const latency = data.latency_ms?.total;
    document.getElementById("agentLatency").textContent = latency ? `${Math.round(latency)} ms` : "--";
    document.getElementById("agentEvidence").textContent = JSON.stringify(data.evidence || {}, null, 2);
  }

  async function askAgent(question) {
    const submit = document.getElementById("agentSubmit");
    submit.disabled = true;
    submit.textContent = "Agent 运行中...";
    renderMessage("user", question);
    try {
      const response = await fetch("/api/agent/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || `HTTP ${response.status}`);
      renderMessage("assistant", data.answer || "No answer returned.");
      renderTrace(data);
    } catch (error) {
      renderMessage(
        "assistant",
        `运行失败：${error.message}\n请确认已通过 FastAPI 启动项目，并配置 ASCEND_API_KEY。静态 GitHub Pages 只能展示原仪表盘，不能调用 Agent 后端。`
      );
    } finally {
      submit.disabled = false;
      submit.textContent = "运行 Agent";
    }
  }

  function wireAgent() {
    const form = document.getElementById("agentForm");
    const input = document.getElementById("agentQuestion");
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const question = input.value.trim();
      if (!question) return;
      input.value = "";
      askAgent(question);
    });

    document.getElementById("agentQuickPrompts").addEventListener("click", (event) => {
      const button = event.target.closest("button[data-prompt]");
      if (!button) return;
      input.value = button.dataset.prompt;
      input.focus();
    });
  }

  function boot() {
    createAgentSection();
    wireAgent();
    checkHealth();
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
