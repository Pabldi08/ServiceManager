# NOTES.md

## Completed Points

1. Stabilize the current base
   - README now points to the real local URL.
   - `settings.json` loading reports clearer errors.
   - Service/action validation has more tests.

2. Improve configuration
   - Hosts can include an optional SSH `port`.
   - Hosts can include an optional SSH `key_path`.
   - Host configuration is validated before running SSH commands.
   - Bun can launch the project with `bun run start`.

3. Automatic service discovery
   - `app/discovery.py` can parse `systemctl list-unit-files` output.
   - The web page can discover services from a selected SSH host.
   - Discovered services are shown before saving.
   - Only user-selected services are registered into `settings.json`.
   - Discovery parsing and settings persistence have tests.

4. Service status dashboard
   - `app/status.py` can parse `systemctl is-active` output.
   - The web page has a read-only status panel for registered services.
   - The dashboard shows service key, unit name, state, and error text.
   - States use simple labels like `active`, `inactive`, `failed`, and `unknown`.
   - Status parsing has tests.

5. Separate backend logic more clearly
   - HTML rendering helpers were moved from `app/web.py` to `app/views.py`.
   - `app/web.py` now focuses more on HTTP request handling.
   - The main view now uses one selected host for service actions, discovery, and status checks.
   - The service-management view shows every registered service with the five allowed action buttons.

6. UI-managed persistence and accessibility
   - Runtime configuration now starts fresh and is managed from the web UI.
   - Hosts can be added with `usuario@host` or `usuario@host:puerto`.
   - Host and service selections are persisted in `data/service_manager.json`.
   - Service listing uses `systemctl list-units --type=service --no-pager --no-legend`.
   - Services are manually selected by the user before being managed.
   - The UI includes Light, Dark, and System theme modes saved in `localStorage`.

7. Safer shared command layer
   - SSH command construction and execution remain centralized in `app/remote.py`.
   - Remote commands are validated as non-empty argument lists.
   - Command execution returns one consistent result shape.
   - Command construction remains separate from execution.
   - Tests cover command validation and result formatting.

8. Improve the web interface
   - The heading was refactored into a `<nav>` layout using Flexbox.
   - The theme dropdown was replaced with a three-option toggle.
   - Light, Dark, and System theme states use descriptive SVG icons.
   - Theme selection continues to persist in `localStorage`.
   - The navigation and theme toggle remain responsive on mobile.

## Next Point: Add Logs and Action History

Goal: record service actions so the user can review recent activity.

Suggested steps:

1. Save each service action with host, service, action, return code, and timestamp.
2. Store history in local app data without passwords or secrets.
3. Show recent actions in the interface.
4. Keep the log readable and beginner-friendly.
5. Add tests for history persistence helpers.

Important safety rule: logs should not store sensitive command output unless explicitly needed.

## Completed Plan Details

### Improve the Web Interface

Goal: make the interface clearer and easier to use as the app grows.

Suggested steps:

1. Review the page layout now that hosts, services, status, and theme controls exist.
2. Group related actions more clearly.
3. Improve empty states for first-time users.
4. Keep mobile layout readable.
5. Avoid visual complexity that makes the project harder to understand.

Important safety rule: UI improvements should not add new service actions or dangerous commands.

### Safer Shared Command Layer

Goal: make SSH command execution safer and easier to reuse as more features are added.

Suggested steps:

1. Review `app/remote.py` and keep all SSH execution in one place.
2. Use one result format for all remote commands.
3. Keep command construction separate from command execution.
4. Add tests for command construction where useful.
5. Avoid adding dangerous commands or broad shell execution.

Important safety rule: do not use `shell=True` for remote command building. Keep commands as argument lists.

### Separate Backend Logic More Clearly

Goal: keep backend modules small and easier to test as the app grows.

Suggested steps:

1. Review `app/web.py` and identify logic that belongs outside the web layer.
2. Keep request handling in `app/web.py`.
3. Move reusable service/status/discovery helpers into focused backend modules only when needed.
4. Avoid a large refactor; make small extractions that improve readability.
5. Add or update tests when logic is moved.

Important safety rule: do not change the app behavior during this cleanup. The goal is organization, not new features.

### Service Status Dashboard

Goal: show the current state of registered services for a selected host.

Suggested steps:

1. Add a backend function that runs this command for one service:

   ```bash
   systemctl is-active service-name
   ```

2. Add a function that checks every registered service for a selected host.
3. Show a table in the web page with service name and state.
4. Use simple labels such as `active`, `inactive`, `failed`, or `unknown`.
5. Add a refresh button.
6. Keep the existing manual action form available.
7. Add tests for parsing service states.

Important safety rule: the dashboard should only read service state. It should not start, stop, restart, enable, or disable services automatically.

### Automatic Service Discovery

Goal: detect services from a Linux device connected through SSH and allow the user to register selected services.

Suggested steps:

1. Create `app/discovery.py`.
2. Add a function that runs this command remotely:

   ```bash
   systemctl list-unit-files --type=service --no-pager --no-legend
   ```

3. Parse only valid `.service` unit names from the command output.
4. Add a simple web action to discover services for a selected host.
5. Show discovered services in the web page.
6. Let the user choose which discovered services should be saved.
7. Save confirmed services into `settings.json`.
8. Add tests for parsing discovered service output.

Important safety rule: discovery should not automatically allow every remote service. The user should confirm which services become manageable.

## Later Points

7. Add persistence for discovered services.
