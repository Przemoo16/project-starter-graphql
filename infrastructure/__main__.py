# ruff: noqa: F401
import resources.network
import resources.services
from pulumi import export
from resources.cache import cache_endpoint
from resources.database import database_endpoint
from resources.lb import lb_dns_name
from resources.repositories import (
    backend_repository_url,
    frontend_repository_url,
    proxy_repository_url,
)

export("frontend_repository_url", frontend_repository_url)
export("backend_repository_url", backend_repository_url)
export("proxy_repository_url", proxy_repository_url)

export("database_endpoint", database_endpoint)

export("cache_endpoint", cache_endpoint)

export("lb_dns_name", lb_dns_name)
