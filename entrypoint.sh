#!/bin/bash

set -e

# On PROD, we run migrations at startup unless explicitly disabled.
# If disabled, this command must be run manually for the application to function correctly after a model update.
if [ "$ENV" == "PROD" ] && [ "${DISABLE_MIGRATION_SCRIPT_ON_PRODUCTION}" != "true" ]; then
    python3 manage.py migrate
fi

# On PROD, we always collect statics
if [ "$ENV" == "PROD" ]; then
    python3 manage.py collectstatic --no-input
fi

# Run the command
exec $@
