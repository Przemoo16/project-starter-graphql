# pylint: disable=unused-import
# ruff: noqa: F401
import resources.ecs
import resources.ecs_access
import resources.network
from pulumi import export
from resources.alb import lb_dns_name
from resources.ecr import (
    backend_repository_url,
    frontend_repository_url,
    proxy_repository_url,
)
from resources.elasticache import cache_endpoint
from resources.rds import database_endpoint

export("frontend_repository_url", frontend_repository_url)
export("backend_repository_url", backend_repository_url)
export("proxy_repository_url", proxy_repository_url)

export("database_endpoint", database_endpoint)

export("cache_endpoint", cache_endpoint)

export("lb_dns_name", lb_dns_name)
