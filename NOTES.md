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

## Next Point: Service Status Dashboard

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

## Completed Plan Details

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

4. Separate backend logic more clearly as the project grows.
5. Add a safer shared command layer for SSH execution.
6. Improve the web interface.
7. Add persistence for discovered services.
8. Add logs and action history.
