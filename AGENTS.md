# AGENTS.md

## Project overview

This is a Python learning project for managing Linux services over SSH.

The goal is to build a simple application that can connect to a remote Linux machine, such as a Raspberry Pi, and manage services using commands like `systemctl`.

The user is learning Python, so changes should be progressive, simple, and well explained.

## Current goals

- Avoid hardcoded SSH/service logic.
- Separate SSH connection logic from service-management logic.
- Keep `run.py` as the main entry point.
- Build the backend first.
- Add a simple interface later.

## Development style

- Make small, incremental changes.
- Do not refactor the whole project at once.
- Prefer simple Python over overly advanced patterns.
- Explain why each new file, class, or function is being created.
- Keep code readable and beginner-friendly.
- Use type hints when they help, but do not overcomplicate the code.
- After completing each project plan point, update `NOTES.md` with the progress made and the next point to follow.

## Architecture preferences

Suggested structure

service_manager/
  ssh_client.py
  service_manager.py
  config.py
run.py

ssh_client.py should handle SSH connections.

service_manager.py should contain logic related to Linux services.

config.py may contain temporary configuration while the app is still in early development.

run.py should act as the main launcher.

##Commands

Run the project with:
python3 run.py

Or with Bun:
bun run start

Run tests with:
python3 -m unittest

Or with Bun:
bun run test


##Safety rules
- Do not delete files unless explicitly requested.
- Do not overwrite large parts of the project without explaining the plan first.
- Do not commit or expose secrets.
- Never store SSH passwords, API keys, or tokens directly in code.
- Prefer environment variables or a .env file for secrets.
- Do not run destructive remote commands such as rm -rf, shutdown, reboot, or service-disabling commands unless explicitly requested.

##SSH rules

The project may connect to a Raspberry Pi or other Linux server by SSH.

When implementing SSH functionality:

- Keep connection parameters configurable.
- Do not hardcode the remote host permanently.
- Do not hardcode passwords.
- Allow future support for SSH keys.
- Keep command execution isolated in one class or module.

##Testing and debugging

When making changes:

- First explain the intended change.
- Then modify only the necessary files.
- After changing code, suggest the exact command to test it.
- If there is an error, focus on fixing that specific error before adding new features.
