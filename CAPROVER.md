# MoneyPrinterTurbo on CapRover

This fork contains two CapRover deployment options:

- `captain-definition` — deploys only the upstream WebUI image.
- `caprover-one-click.yml` — recommended; deploys the WebUI plus the internal API and persistent configuration/storage.

## Recommended: One-Click App

Use `caprover-one-click.yml` as a custom CapRover One-Click App template.

The template uses the official upstream image:

`ghcr.io/harry0703/moneyprinterturbo:latest`

It creates two services:

- `$$cap_appname` — Streamlit WebUI, container port `8501`, exposed through CapRover.
- `$$cap_appname-api` — FastAPI service, port `8080`, internal only.

Both services share one named Docker volume. The startup command places these persistent resources in it:

- `/persistent/config.toml`
- `/persistent/storage/`

The application paths are linked to those persistent resources at startup. This prevents provider settings, API keys and generated files from disappearing when the containers are replaced or updated.

## Installation

1. Open CapRover.
2. Go to **Apps > One-Click Apps/Databases**.
3. Use the custom One-Click template option and paste/load the contents of `caprover-one-click.yml`.
4. Choose an app name, for example `moneyprinterturbo`.
5. Keep image tag `latest` unless you intentionally want to pin another upstream tag.
6. Deploy.
7. Enable HTTPS on the WebUI application.
8. Recommended: enable CapRover HTTP Basic Auth because the MoneyPrinterTurbo WebUI should not be left openly accessible on the internet.

## Configuration

Configure LLM, video-material, TTS and publishing providers from MoneyPrinterTurbo after deployment. Do not put real API keys in this repository.

The internal API can be reached by other CapRover services at:

`srv-captain--<appname>-api:8080`

It is deliberately not exposed publicly by the template.

## Updates

With the default `latest` image tag, redeploying the services makes CapRover pull/use the current upstream image. Persistent configuration and generated files remain in the named volume.

For reproducible deployments, replace `latest` with a known upstream image tag when available.

## Upstream

https://github.com/harry0703/MoneyPrinterTurbo
