from pulumi_aws.servicediscovery import (
    PrivateDnsNamespace,
    Service,
    ServiceDnsConfigArgs,
    ServiceDnsConfigDnsRecordArgs,
)

from resources.network import network_id

_private_dns_namespace = PrivateDnsNamespace("local", vpc=network_id)


def _create_service(name: str) -> Service:
    return Service(
        name,
        dns_config=ServiceDnsConfigArgs(
            namespace_id=_private_dns_namespace.id,
            dns_records=[
                ServiceDnsConfigDnsRecordArgs(
                    ttl=10,
                    type="A",
                )
            ],
            routing_policy="MULTIVALUE",
        ),
    )


_frontend_service = _create_service("frontend")
_backend_service = _create_service("backend")
_proxy_service = _create_service("proxy")

private_dns_namespace_name = _private_dns_namespace.name

frontend_service_arn = _frontend_service.arn
frontend_service_name = _frontend_service.name
backend_service_arn = _backend_service.arn
backend_service_name = _backend_service.name
proxy_service_arn = _proxy_service.arn
proxy_service_name = _proxy_service.name
