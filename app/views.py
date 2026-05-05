from html import escape
from pathlib import Path

from app.config import getHosts
from app.services import getAllowedActions, getAllowedServices


BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = BASE_DIR / "templates" / "index.html"


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

    statusClass = "result-ok" if result["returncode"] == 0 else "result-error"
    stdout = escape(result["stdout"]) or "(sin salida)"
    stderr = escape(result["stderr"]) or "(sin error)"

    return f"""
    <section class="result {statusClass}">
      <div class="result-header">
        <h2>Resultado</h2>
        <span>codigo {result["returncode"]}</span>
      </div>
      <label>Salida</label>
      <pre>{stdout}</pre>
      <label>Error</label>
      <pre>{stderr}</pre>
    </section>
    """


def renderHostList(hosts):
    if not hosts:
        return "<p>No hay hosts registrados todavia.</p>"

    items = []
    for hostName, hostData in hosts.items():
        target = f"{hostData['user']}@{hostData['host']}:{hostData.get('port', 22)}"
        items.append(f"<li><strong>{escape(hostName)}</strong> <span>{escape(target)}</span></li>")

    return f"<ul class=\"host-list\">{''.join(items)}</ul>"


def renderServiceList(selectedHost):
    if not selectedHost:
        return "<p>Anade un host para empezar a gestionar servicios.</p>"

    services = getAllowedServices(selectedHost)
    actions = getAllowedActions()

    if not services:
        return "<p>No hay servicios registrados todavia.</p>"

    rows = []

    for serviceKey, serviceName in services.items():
        buttons = []

        for action in actions:
            buttons.append(f"""
              <button type="submit" name="action" value="{escape(action)}">
                {escape(action)}
              </button>
            """)

        rows.append(f"""
          <article class="service-card">
            <div>
              <h3>{escape(serviceKey)}</h3>
              <p>{escape(serviceName)}</p>
            </div>
            <form method="post" action="/run" class="service-actions">
              <input type="hidden" name="host" value="{escape(selectedHost)}">
              <input type="hidden" name="service" value="{escape(serviceKey)}">
              {''.join(buttons)}
            </form>
          </article>
        """)

    return "".join(rows)


def renderDiscoveredServices(selectedHost=None, discoveredServices=None):
    if not discoveredServices:
        return ""

    serviceInputs = []
    registeredServices = set(getAllowedServices(selectedHost).values())

    for serviceName in discoveredServices:
        checked = "" if serviceName in registeredServices else " checked"
        disabled = " disabled" if serviceName in registeredServices else ""
        badge = " <span>registrado</span>" if serviceName in registeredServices else ""
        escapedService = escape(serviceName)

        serviceInputs.append(f"""
          <label class="check-row">
            <input type="checkbox" name="services" value="{escapedService}"{checked}{disabled}>
            <span>{escapedService}{badge}</span>
          </label>
        """)

    return f"""
    <section class="panel discovery-results">
      <h2>Servicios disponibles</h2>
      <p>Selecciona manualmente los servicios que quieres gestionar en este host.</p>
      <form method="post" action="/register-services" class="discovery-list">
        <input type="hidden" name="host" value="{escape(selectedHost or '')}">
        {''.join(serviceInputs)}
        <button type="submit">Guardar seleccionados</button>
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
            <td>{serviceKey}</td>
            <td>{serviceName}</td>
            <td><span class="state state-{state}">{state}</span></td>
            <td>{stderr}</td>
          </tr>
        """)

    return f"""
    <section class="panel status-results">
      <h2>Estado de servicios</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Clave</th>
              <th>Servicio</th>
              <th>Estado</th>
              <th>Error</th>
            </tr>
          </thead>
          <tbody>
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
    html = html.replace("{{ service_list }}", renderServiceList(selectedHost))
    html = html.replace(
        "{{ discovered_services }}",
        renderDiscoveredServices(selectedHost, discoveredServices),
    )
    html = html.replace("{{ status_dashboard }}", renderStatusDashboard(statuses))
    html = html.replace("{{ result }}", renderResult(result))
    return html
