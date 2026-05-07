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

TRASH_ICON = """
  <svg class="action-icon" aria-hidden="true" viewBox="0 0 24 24" focusable="false">
    <path d="M4 7h16"></path>
    <path d="M10 11v6"></path>
    <path d="M14 11v6"></path>
    <path d="M6 7l1 14h10l1-14"></path>
    <path d="M9 7V4h6v3"></path>
  </svg>
"""

PLUS_ICON = """
  <svg class="action-icon" aria-hidden="true" viewBox="0 0 24 24" focusable="false">
    <path d="M12 5v14"></path>
    <path d="M5 12h14"></path>
  </svg>
"""


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


def renderInlineStatusResult(result):
    if result is None:
        return ""

    statusClass = "state-active" if result["returncode"] == 0 else "state-failed"

    stdout = escape(result["stdout"].strip()) if result["stdout"] else "(sin salida)"
    stderr = escape(result["stderr"].strip()) if result["stderr"] else ""

    errorBlock = ""

    if stderr:
        errorBlock = f"""
        <div class="min-w-0">
          <p class="text-[10px] font-bold uppercase tracking-wide text-[var(--muted)]">
            stderr
          </p>

          <pre class="mt-1 max-h-32 max-w-full overflow-auto whitespace-pre-wrap break-all rounded-lg bg-[var(--surface)] p-2 text-[9px] leading-tight text-[var(--text)]">{stderr}</pre>
        </div>
        """

    return f"""
    <section class="status-action-result mt-3 max-w-full overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--surface-soft)] p-3" aria-live="polite">
      <div class="flex min-w-0 items-center justify-between gap-2">
        <h4 class="truncate text-sm font-bold text-[var(--text)]">
          Status result
        </h4>
      </div>

      <div class="mt-2 grid gap-2">
        <div class="min-w-0">
          <p class="text-[10px] font-bold uppercase tracking-wide text-[var(--muted)]">
            stdout
          </p>

          <pre class="mt-1 max-h-32 max-w-full overflow-auto whitespace-pre-wrap break-all rounded-lg bg-[var(--surface)] p-2 text-[10px] leading-tight text-[var(--text)]">{stdout}</pre>
        </div>

        {errorBlock}
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
        escapedHost = escape(hostName)
        items.append(f"""
        <li class="flex items-center justify-between gap-3 rounded-2xl border border-[var(--border)] bg-[var(--surface-soft)] p-3">
          <div class="min-w-0">
            <strong class="block truncate text-sm text-[var(--text)]">{escapedHost}</strong>
            <span class="mt-1 block truncate text-xs text-[var(--muted)]">{escape(target)}</span>
          </div>
          <form method="post" action="/delete-host">
            <input type="hidden" name="host" value="{escapedHost}">
            <button class="icon-danger-button" type="submit" aria-label="Eliminar host {escapedHost}" title="Eliminar host">
              {TRASH_ICON}
            </button>
          </form>
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
    dotClasses = {
        "active": "service-status-dot-active",
        "activating": "service-status-dot-pending",
        "deactivating": "service-status-dot-pending",
        "unknown": "service-status-dot-unknown",
    }
    dotClass = dotClasses.get(state, "service-status-dot-inactive")
    label = state if state != "unknown" else "desconocido"

    return f'<span class="service-status-dot {dotClass}" title="Servicio {label}" aria-label="Servicio {label}"></span>'


def renderServiceList(selectedHost, statuses=None, selected=None, result=None):
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
        inlineStatusResult = ""

        if selected and selected.get("service") == serviceKey and selected.get("action") == "status":
            inlineStatusResult = renderInlineStatusResult(result)

        for action in actions:
            if action == "is-active":
                continue

            buttons.append(renderActionButton(action))

        rows.append(f"""
          <article class="rounded-2xl border border-[var(--border)] bg-[var(--surface-soft)] p-4">
            <div class="grid gap-3 lg:grid-cols-[minmax(10rem,1fr)_auto] lg:items-center">
              <div class="flex min-w-0 items-center gap-3">
                <div>
                  {renderServiceStatusDot(serviceKey, statuses)}
                </div>
                <div class="min-w-0">
                  <h3 class="truncate text-base font-bold text-[var(--text)]">{escape(serviceKey)}</h3>
                  <p class="mt-1 truncate font-mono text-xs text-[var(--muted)]">{escape(serviceName)}</p>
                </div>
              </div>
              <div class="flex flex-wrap gap-2 lg:justify-end">
                <form method="post" action="/run" class="flex flex-wrap gap-2 lg:justify-end">
                  <input type="hidden" name="host" value="{escape(selectedHost)}">
                  <input type="hidden" name="service" value="{escape(serviceKey)}">
                  {''.join(buttons)}
                </form>
              </div>
            </div>
            {inlineStatusResult}
          </article>
        """)

    return f"<div class=\"grid gap-3\">{''.join(rows)}</div>"


def renderHiddenDiscoveredServices(discoveredServices):
    return "".join(
        f'<input type="hidden" name="discovered_services" value="{escape(serviceName)}">'
        for serviceName in discoveredServices or []
    )


def renderServiceManagementDialog(selectedHost=None, discoveredServices=None):
    if discoveredServices is None:
        return ""

    registeredServices = getAllowedServices(selectedHost) if selectedHost else {}
    registeredNames = set(registeredServices.values())
    availableServices = [
        serviceName for serviceName in discoveredServices if serviceName not in registeredNames
    ]
    hiddenDiscoveredServices = renderHiddenDiscoveredServices(discoveredServices)
    includedRows = []
    availableRows = []

    for serviceKey, serviceName in registeredServices.items():
        escapedKey = escape(serviceKey)
        escapedService = escape(serviceName)
        includedRows.append(f"""
          <li class="service-dialog-row">
            <div class="min-w-0 flex-1">
              <strong class="block truncate text-sm text-[var(--text)]">{escapedKey}</strong>
              <span class="block truncate font-mono text-xs text-[var(--muted)]">{escapedService}</span>
            </div>
            <form class="shrink-0" method="post" action="/delete-service">
              <input type="hidden" name="host" value="{escape(selectedHost or '')}">
              <input type="hidden" name="service" value="{escapedKey}">
              {hiddenDiscoveredServices}
              <button class="icon-danger-button" type="submit" aria-label="Remove service {escapedKey}" title="Remove service">
                {TRASH_ICON}
              </button>
            </form>
          </li>
        """)

    for serviceName in availableServices:
        escapedService = escape(serviceName)
        escapedKey = escape(serviceName.removesuffix(".service"))
        availableRows.append(f"""
          <li class="service-dialog-row">
            <div class="min-w-0 flex-1">
              <strong class="block truncate text-sm text-[var(--text)]">{escapedKey}</strong>
              <span class="block truncate font-mono text-xs text-[var(--muted)]">{escapedService}</span>
            </div>
            <form class="shrink-0" method="post" action="/register-services">
              <input type="hidden" name="host" value="{escape(selectedHost or '')}">
              <input type="hidden" name="services" value="{escapedService}">
              {hiddenDiscoveredServices}
              <button class="icon-add-button" type="submit" aria-label="Add service {escapedService}" title="Add service">
                {PLUS_ICON}
              </button>
            </form>
          </li>
        """)

    if not includedRows:
        includedRows.append("""
          <li class="rounded-2xl border border-dashed border-[var(--border)] p-4 text-sm text-[var(--muted)]">No included services yet.</li>
        """)

    if not availableRows:
        availableRows.append("""
          <li class="rounded-2xl border border-dashed border-[var(--border)] p-4 text-sm text-[var(--muted)]">No new services available.</li>
        """)

    return f"""
    <dialog id="services-dialog" class="dialog-panel w-[min(94vw,58rem)]" data-auto-open-dialog>
      <div class="grid max-h-[85vh] gap-5 overflow-hidden p-5">
        <div class="flex items-start justify-between gap-4">
          <div>
            <h2 class="text-lg font-bold text-[var(--text)]">Manage services</h2>
            <p class="mt-1 text-sm text-[var(--muted)]">Services found on {escape(selectedHost or 'the selected host')}.</p>
          </div>
          <button class="btn-secondary min-h-9 px-3" type="button" data-dialog-close>Close</button>
        </div>

        <div class="grid min-w-0 min-h-0 gap-4 md:grid-cols-2">
          <section class="service-dialog-section">
            <h3 class="text-sm font-bold uppercase tracking-wide text-[var(--muted)]">Included</h3>
            <ul class="mt-3 grid max-h-[55vh] min-w-0 gap-2 overflow-y-auto overflow-x-hidden pr-1">
              {''.join(includedRows)}
            </ul>
          </section>

          <section class="service-dialog-section">
            <h3 class="text-sm font-bold uppercase tracking-wide text-[var(--muted)]">Available to add</h3>
            <ul class="mt-3 grid max-h-[55vh] min-w-0 gap-2 overflow-y-auto overflow-x-hidden pr-1">
              {''.join(availableRows)}
            </ul>
          </section>
        </div>
      </div>
    </dialog>
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
    html = html.replace("{{ service_list }}", renderServiceList(selectedHost, statuses, selected, result))
    html = html.replace(
        "{{ discovered_services }}",
        renderServiceManagementDialog(selectedHost, discoveredServices),
    )
    html = html.replace("{{ status_dashboard }}", renderStatusDashboard(statuses))
    html = html.replace("{{ result }}", "" if selected.get("action") == "status" else renderResult(result))
    return html
