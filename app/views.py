from html import escape
from pathlib import Path

from app.config import getHosts
from app.services import getAllowedActions, getAllowedServices


BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = BASE_DIR / "templates" / "index.html"

ACTION_ICONS = {
    "start": """
      <svg class="action-icon" aria-hidden="true" viewBox="0 0 24 24" focusable="false">
        <path d="M8 5.5v13l10-6.5-10-6.5Z"></path>
      </svg>
    """,
    "stop": """
      <svg class="action-icon" aria-hidden="true" viewBox="0 0 24 24" focusable="false">
        <rect x="7" y="7" width="10" height="10" rx="1.5"></rect>
      </svg>
    """,
    "restart": """
      <svg class="action-icon" aria-hidden="true" viewBox="0 0 24 24" focusable="false">
        <path d="M19 12a7 7 0 1 1-2.05-4.95"></path>
        <path d="M19 4v5h-5"></path>
      </svg>
    """,
}


def buildOptions(items, selectedValue=None):
    options = []

    for value, label in items:
        selected = " selected" if value == selectedValue else ""
        options.append(
            f'<option value="{escape(value)}"{selected}>{escape(label)}</option>'
        )

    return "\n".join(options)


def renderResult(result):
    if result is None:
        return ""

    statusClass = "border-emerald-500/50" if result["returncode"] == 0 else "border-red-500/50"
    stdout = escape(result["stdout"]) or "(sin salida)"
    stderr = escape(result["stderr"]) or "(sin error)"

    return f"""
    <section class="panel border-l-4 {statusClass}" aria-live="polite">
      <div class="flex items-center justify-between gap-3">
        <h2 class="text-base font-bold text-[var(--text)]">Result</h2>
        <span class="rounded-full bg-[var(--surface-soft)] px-3 py-1 text-xs font-bold text-[var(--muted)]">code {result["returncode"]}</span>
      </div>
      <div class="mt-4 grid gap-3 md:grid-cols-2">
        <div>
          <p class="text-xs font-bold uppercase tracking-wide text-[var(--muted)]">stdout</p>
          <pre class="mt-2 max-h-56 overflow-auto rounded-xl bg-[var(--surface-soft)] p-3 text-xs text-[var(--text)]">{stdout}</pre>
        </div>
        <div>
          <p class="text-xs font-bold uppercase tracking-wide text-[var(--muted)]">stderr</p>
          <pre class="mt-2 max-h-56 overflow-auto rounded-xl bg-[var(--surface-soft)] p-3 text-xs text-[var(--text)]">{stderr}</pre>
        </div>
      </div>
    </section>
    """


def renderHostList(hosts):
    if not hosts:
        return """
        <div class="rounded-2xl border border-dashed border-[var(--border)] bg-[var(--surface-soft)] p-4 text-sm text-[var(--muted)]">
          No hosts yet. Add one with the + button.
        </div>
        """

    items = []
    for hostName, hostData in hosts.items():
        target = f"{hostData['user']}@{hostData['host']}:{hostData.get('port', 22)}"
        items.append(f"""
        <li class="rounded-2xl border border-[var(--border)] bg-[var(--surface-soft)] p-3">
          <strong class="block truncate text-sm text-[var(--text)]">{escape(hostName)}</strong>
          <span class="mt-1 block truncate text-xs text-[var(--muted)]">{escape(target)}</span>
        </li>
        """)

    return f"<ul class=\"grid gap-2\">{''.join(items)}</ul>"


def renderActionButton(action):
    escapedAction = escape(action)

    if action in ACTION_ICONS:
        return f"""
              <button class="action-icon-button" type="submit" name="action" value="{escapedAction}" aria-label="{escapedAction}" title="{escapedAction}">
                {ACTION_ICONS[action]}
                <span class="sr-only">{escapedAction}</span>
              </button>
        """

    return f"""
              <button class="btn-secondary min-h-9 px-3 text-xs" type="submit" name="action" value="{escapedAction}">
                {escapedAction}
              </button>
    """


def renderServiceStatusDot(serviceKey, statuses=None):
    statusByKey = {status["key"]: status for status in statuses or []}
    state = statusByKey.get(serviceKey, {}).get("state", "unknown")
    dotClass = "service-status-dot-active" if state == "active" else "service-status-dot-inactive"
    label = "activo" if state == "active" else "inactivo"

    return f'<span class="service-status-dot {dotClass}" title="Servicio {label}" aria-label="Servicio {label}"></span>'


def renderServiceList(selectedHost, statuses=None):
    if not selectedHost:
        return """
        <div class="rounded-2xl border border-dashed border-[var(--border)] bg-[var(--surface-soft)] p-6 text-center">
          <p class="text-sm font-semibold text-[var(--text)]">No host selected</p>
          <p class="mt-1 text-sm text-[var(--muted)]">Add or select a host to manage services.</p>
        </div>
        """

    services = getAllowedServices(selectedHost)
    actions = getAllowedActions()

    if not services:
        return """
        <div class="rounded-2xl border border-dashed border-[var(--border)] bg-[var(--surface-soft)] p-6 text-center">
          <p class="text-sm font-semibold text-[var(--text)]">No managed services</p>
          <p class="mt-1 text-sm text-[var(--muted)]">List available services and save the ones you want to manage.</p>
        </div>
        """

    rows = []

    for serviceKey, serviceName in services.items():
        buttons = []

        for action in actions:
            if action == "is-active":
                continue

            buttons.append(renderActionButton(action))

        rows.append(f"""
          <article class="grid gap-3 rounded-2xl border border-[var(--border)] bg-[var(--surface-soft)] p-4 lg:grid-cols-[minmax(10rem,1fr)_minmax(0,2fr)] lg:items-center">
            <div class="flex min-w-0 items-center gap-3">
              <div>
                {renderServiceStatusDot(serviceKey, statuses)}
              </div>
              <div class="min-w-0">
                <h3 class="truncate text-base font-bold text-[var(--text)]">{escape(serviceKey)}</h3>
              <p class="mt-1 truncate font-mono text-xs text-[var(--muted)]">{escape(serviceName)}</p>
              </div>
            </div>
            <form method="post" action="/run" class="flex flex-wrap gap-2 lg:justify-end">
              <input type="hidden" name="host" value="{escape(selectedHost)}">
              <input type="hidden" name="service" value="{escape(serviceKey)}">
              {''.join(buttons)}
            </form>
          </article>
        """)

    return f"<div class=\"grid gap-3\">{''.join(rows)}</div>"


def renderDiscoveredServices(selectedHost=None, discoveredServices=None):
    if not discoveredServices:
        return ""

    serviceInputs = []
    registeredServices = set(getAllowedServices(selectedHost).values())

    for serviceName in discoveredServices:
        checked = "" if serviceName in registeredServices else " checked"
        disabled = " disabled" if serviceName in registeredServices else ""
        badge = " <span class=\"ml-2 rounded-full bg-[var(--surface-soft)] px-2 py-0.5 text-xs font-bold text-[var(--muted)]\">saved</span>" if serviceName in registeredServices else ""
        escapedService = escape(serviceName)

        serviceInputs.append(f"""
          <label class="flex items-center gap-3 border-b border-[var(--border)] py-3 text-sm text-[var(--text)] last:border-0">
            <input class="size-4 accent-[var(--primary)]" type="checkbox" name="services" value="{escapedService}"{checked}{disabled}>
            <span class="min-w-0 truncate">{escapedService}{badge}</span>
          </label>
        """)

    return f"""
    <section class="panel">
      <div class="mb-3 flex items-center justify-between gap-3">
        <div>
          <h2 class="text-lg font-bold text-[var(--text)]">Available services</h2>
          <p class="text-sm text-[var(--muted)]">Choose manually before saving.</p>
        </div>
      </div>
      <form method="post" action="/register-services">
        <input type="hidden" name="host" value="{escape(selectedHost or '')}">
        <div class="max-h-96 overflow-auto rounded-2xl border border-[var(--border)] px-4">
          {''.join(serviceInputs)}
        </div>
        <button class="btn-primary mt-4" type="submit">Save selected</button>
      </form>
    </section>
    """


def renderStatusDashboard(statuses=None):
    if not statuses:
        return ""

    rows = []

    for status in statuses:
        serviceKey = escape(status["key"])
        serviceName = escape(status["service"])
        state = escape(status["state"])
        stderr = escape(status["stderr"]) or "-"

        rows.append(f"""
          <tr>
            <td class="px-4 py-3 font-semibold text-[var(--text)]">{serviceKey}</td>
            <td class="px-4 py-3 font-mono text-xs text-[var(--muted)]">{serviceName}</td>
            <td class="px-4 py-3"><span class="inline-flex items-center gap-2 rounded-full border px-2.5 py-1 text-xs font-bold state-{state}"><span aria-hidden="true">●</span>{state}</span></td>
            <td class="px-4 py-3 text-xs text-[var(--muted)]">{stderr}</td>
          </tr>
        """)

    return f"""
    <section class="panel">
      <h2 class="text-lg font-bold text-[var(--text)]">Service status</h2>
      <div class="mt-4 overflow-x-auto rounded-2xl border border-[var(--border)]">
        <table class="min-w-full text-left text-sm">
          <thead class="bg-[var(--surface-soft)] text-xs uppercase tracking-wide text-[var(--muted)]">
            <tr>
              <th class="px-4 py-3">Key</th>
              <th class="px-4 py-3">Service</th>
              <th class="px-4 py-3">State</th>
              <th class="px-4 py-3">Error</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-[var(--border)]">
            {''.join(rows)}
          </tbody>
        </table>
      </div>
    </section>
    """


def renderIndex(selected=None, result=None, discoveredServices=None, statuses=None):
    selected = selected or {}
    hosts = [(hostName, hostName) for hostName in getHosts()]
    selectedHost = selected.get("host") or (hosts[0][0] if hosts else "")

    html = TEMPLATE_PATH.read_text(encoding="utf-8")
    html = html.replace("{{ host_options }}", buildOptions(hosts, selectedHost))
    html = html.replace("{{ selected_host }}", escape(selectedHost))
    html = html.replace("{{ host_list }}", renderHostList(getHosts()))
    html = html.replace("{{ service_list }}", renderServiceList(selectedHost, statuses))
    html = html.replace(
        "{{ discovered_services }}",
        renderDiscoveredServices(selectedHost, discoveredServices),
    )
    html = html.replace("{{ status_dashboard }}", renderStatusDashboard(statuses))
    html = html.replace("{{ result }}", renderResult(result))
    return html
