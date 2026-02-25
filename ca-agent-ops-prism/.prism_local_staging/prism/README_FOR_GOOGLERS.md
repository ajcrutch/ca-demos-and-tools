# Setup instructions for Googlers (gLinux)

Prism uses Docker for its local database setup and `uv` for dependency
management. Follow these instructions to set up your environment.

## 1. Install Docker

On gLinux, please follow the official internal instructions to install Docker: 👉
**[go/installdocker](https://goto.google.com/installdocker)** .

> [!CAUTION] Do NOT use standard upstream Docker installation guides. Use the
> gLinux-specific guide above to ensure compatibility with Google's internal
> network.

## 2. Setup Database

Googlers need to run the database setup script with the `--sudo` option
to manage Docker containers correctly (unless they have sudo-less docker setup):

```bash
./scripts/setup_postgres.sh --sudo
```

## 3. Install uv

Prism uses `uv` for dependency management. Install it using the following
command:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

This will typically install `uv` to `~/.local/bin/uv`. Ensure this directory is
in your `PATH`.

## 4. OSS Safety & Code Guidelines

This project is mirrored to Open Source. To maintain security and compliance,
follow these rules:

> [!IMPORTANT] **Avoid Internal References**: Do NOT include any references to
> internal Google resources, cloud tops, internal URLs (e.g., `http://go/`), or
> LDAP usernames in any code or comments that will be exported.

*   **Scrubbing**: While Copybara performs basic scrubbing, it is your
    responsibility to ensure no sensitive data is committed.
*   **PRs**: Ensure all code changes are reviewed with OSS exposure in mind.

--------------------------------------------------------------------------------

For general project setup, see [README.md](README.md).
