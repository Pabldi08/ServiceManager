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

## Next Point: Automatic Service Discovery

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

3. Add a service status dashboard.
4. Separate backend logic more clearly as the project grows.
5. Add a safer shared command layer for SSH execution.
6. Improve the web interface.
7. Add persistence for discovered services.
8. Add logs and action history.
