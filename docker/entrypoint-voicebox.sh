#!/bin/sh
set -eu

PERSISTENT_DIR="${MPT_PERSISTENT_DIR:-/persistent}"
APP_DIR="/MoneyPrinterTurbo"

mkdir -p "$PERSISTENT_DIR/storage"

# Keep config.toml across image/container updates. If this is the first start,
# seed it from the image's current example configuration.
if [ ! -f "$PERSISTENT_DIR/config.toml" ]; then
    if [ -f "$APP_DIR/config.toml" ] && [ ! -L "$APP_DIR/config.toml" ]; then
        cp "$APP_DIR/config.toml" "$PERSISTENT_DIR/config.toml"
    else
        cp "$APP_DIR/config.example.toml" "$PERSISTENT_DIR/config.toml"
    fi
fi

# MoneyPrinterTurbo expects these paths inside its application directory.
# Point them at CapRover's persistent volume so configuration, API keys and
# generated/downloaded media survive image updates and container recreation.
rm -rf "$APP_DIR/storage"
ln -s "$PERSISTENT_DIR/storage" "$APP_DIR/storage"

rm -f "$APP_DIR/config.toml"
ln -s "$PERSISTENT_DIR/config.toml" "$APP_DIR/config.toml"

exec "$@"
