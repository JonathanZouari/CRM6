#!/bin/sh
# Replace default API URL with the actual backend URL at runtime
if [ -n "$API_BASE_URL" ]; then
    find /usr/share/nginx/html/js -name '*.js' -exec \
        sed -i "s|http://localhost:5000|${API_BASE_URL}|g" {} +
fi
exec "$@"
