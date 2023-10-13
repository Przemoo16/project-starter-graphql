#!/bin/bash

DNS_SERVER=$(grep -i '^nameserver' /etc/resolv.conf | head -n1 | cut -d ' ' -f2)
export DNS_SERVER
export FRONTEND_UPSTREAM="${FRONTEND_UPSTREAM:-"http://frontend"}"
export BACKEND_UPSTREAM="${BACKEND_UPSTREAM:-"http://backend"}"

# shellcheck disable=SC2016
envsubst '$DNS_SERVER $FRONTEND_UPSTREAM $BACKEND_UPSTREAM' < /var/nginx.conf > /etc/nginx/conf.d/default.conf
