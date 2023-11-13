from helpers.string import (
    create_image_name,
    create_token_url_template,
    create_url_from_namespace,
)
from pulumi import Config, Output, ResourceOptions
from pulumi_aws.ecs import (
    ServiceNetworkConfigurationArgs,
    ServiceServiceRegistriesArgs,
)
from pulumi_aws.ssm import Parameter
from pulumi_awsx.awsx import DefaultRoleWithPolicyArgs
from pulumi_awsx.ecs import (
    FargateService,
    FargateServiceTaskDefinitionArgs,
    TaskDefinitionContainerDefinitionArgs,
    TaskDefinitionKeyValuePairArgs,
    TaskDefinitionPortMappingArgs,
    TaskDefinitionSecretArgs,
)

from resources.cache import cache_access_security_group_id, cache_endpoint
from resources.database import (
    database_access_security_group_id,
    database_host,
    database_name,
    database_password_parameter_name,
    database_port,
    database_username_parameter_name,
)
from resources.lb import lb_dns_name, lb_target_group
from resources.network import network_private_subnet_ids
from resources.repositories import (
    backend_repository_url,
    frontend_repository_url,
    proxy_repository_url,
)
from resources.services.cluster import cluster_arn
from resources.services.iam import task_role_arn
from resources.services.security_groups import (
    backend_access_security_group_id,
    backend_security_group_id,
    frontend_access_security_group_id,
    frontend_security_group_id,
    proxy_access_security_group_id,
    proxy_security_group_id,
    scheduler_security_group_id,
    worker_security_group_id,
)
from resources.services.service_discovery import (
    backend_service_arn,
    backend_service_name,
    frontend_service_arn,
    frontend_service_name,
    private_dns_namespace_name,
    proxy_service_arn,
    proxy_service_name,
)

_config = Config()


_frontend_fargate_service = FargateService(
    "frontend",
    cluster=cluster_arn,
    service_registries=ServiceServiceRegistriesArgs(
        registry_arn=frontend_service_arn, container_name="frontend"
    ),
    network_configuration=ServiceNetworkConfigurationArgs(
        subnets=network_private_subnet_ids,
        security_groups=[
            frontend_security_group_id,
            proxy_access_security_group_id,
        ],
    ),
    desired_count=_config.require_int("frontend_service_desired_count"),
    task_definition_args=FargateServiceTaskDefinitionArgs(
        cpu=_config.require("frontend_task_cpu"),
        memory=_config.require("frontend_task_memory"),
        task_role=DefaultRoleWithPolicyArgs(role_arn=task_role_arn),
        execution_role=DefaultRoleWithPolicyArgs(role_arn=task_role_arn),
        container=TaskDefinitionContainerDefinitionArgs(
            name="frontend",
            image=create_image_name(
                frontend_repository_url, _config.require("version")
            ),
            essential=True,
            port_mappings=[
                TaskDefinitionPortMappingArgs(
                    container_port=_config.require_int("frontend_container_port"),
                )
            ],
            environment=[
                TaskDefinitionKeyValuePairArgs(
                    name="SERVER_GRAPHQL_API_URL",
                    value=Output.concat(
                        create_url_from_namespace(
                            proxy_service_name,
                            private_dns_namespace_name,
                        ),
                        "/api/graphql",
                    ),
                ),
            ],
        ),
    ),
)


_auth_private_key_parameter = Parameter(
    "auth_private_key",
    value=_config.require_secret("auth_private_key"),
    type="SecureString",
)
_smtp_user_parameter = Parameter(
    "smtp_user", value=_config.require_secret("smtp_user"), type="SecureString"
)
_smtp_password_parameter = Parameter(
    "smtp_password", value=_config.require_secret("smtp_password"), type="SecureString"
)

_cache_url = Output.concat("redis://", cache_endpoint)
_backend_environment = [
    TaskDefinitionKeyValuePairArgs(name="DB__NAME", value=database_name),
    TaskDefinitionKeyValuePairArgs(name="DB__HOST", value=database_host),
    TaskDefinitionKeyValuePairArgs(name="DB__PORT", value=database_port.apply(str)),
    TaskDefinitionKeyValuePairArgs(name="WORKER__BROKER_URL", value=_cache_url),
    TaskDefinitionKeyValuePairArgs(name="WORKER__RESULT_BACKEND", value=_cache_url),
    TaskDefinitionKeyValuePairArgs(
        name="USER__EMAIL_CONFIRMATION_URL_TEMPLATE",
        value=create_token_url_template(lb_dns_name, "/confirm-email"),
    ),
    TaskDefinitionKeyValuePairArgs(
        name="USER__RESET_PASSWORD_URL_TEMPLATE",
        value=create_token_url_template(lb_dns_name, "/reset-password"),
    ),
    TaskDefinitionKeyValuePairArgs(
        name="USER__AUTH_PUBLIC_KEY", value=_config.require("auth_public_key")
    ),
    TaskDefinitionKeyValuePairArgs(
        name="EMAIL__SMTP_HOST", value=_config.require("smtp_host")
    ),
    TaskDefinitionKeyValuePairArgs(
        name="EMAIL__SMTP_PORT", value=_config.require("smtp_port")
    ),
    TaskDefinitionKeyValuePairArgs(
        name="EMAIL__SENDER", value=_config.require("email_sender")
    ),
]

_backend_secrets = [
    TaskDefinitionSecretArgs(
        name="DB__USERNAME", value_from=database_username_parameter_name
    ),
    TaskDefinitionSecretArgs(
        name="DB__PASSWORD", value_from=database_password_parameter_name
    ),
    TaskDefinitionSecretArgs(
        name="USER__AUTH_PRIVATE_KEY", value_from=_auth_private_key_parameter.name
    ),
    TaskDefinitionSecretArgs(
        name="EMAIL__SMTP_USER", value_from=_smtp_user_parameter.name
    ),
    TaskDefinitionSecretArgs(
        name="EMAIL__SMTP_PASSWORD", value_from=_smtp_password_parameter.name
    ),
]


_worker_fargate_service = FargateService(
    "worker",
    cluster=cluster_arn,
    network_configuration=ServiceNetworkConfigurationArgs(
        subnets=network_private_subnet_ids,
        security_groups=[
            worker_security_group_id,
            database_access_security_group_id,
            cache_access_security_group_id,
        ],
    ),
    desired_count=_config.require_int("worker_service_desired_count"),
    task_definition_args=FargateServiceTaskDefinitionArgs(
        cpu=_config.require("worker_task_cpu"),
        memory=_config.require("worker_task_memory"),
        task_role=DefaultRoleWithPolicyArgs(role_arn=task_role_arn),
        execution_role=DefaultRoleWithPolicyArgs(role_arn=task_role_arn),
        container=TaskDefinitionContainerDefinitionArgs(
            name="worker",
            image=create_image_name(backend_repository_url, _config.require("version")),
            essential=True,
            port_mappings=[
                TaskDefinitionPortMappingArgs(
                    container_port=_config.require_int("worker_container_port"),
                )
            ],
            command=_config.require_object("worker_container_command"),
            environment=_backend_environment,
            secrets=_backend_secrets,
        ),
    ),
)


if _config.require_bool("scheduler_service_enabled"):
    FargateService(
        "scheduler",
        cluster=cluster_arn,
        network_configuration=ServiceNetworkConfigurationArgs(
            subnets=network_private_subnet_ids,
            security_groups=[
                scheduler_security_group_id,
                database_access_security_group_id,
                cache_access_security_group_id,
            ],
        ),
        desired_count=_config.require_int("scheduler_service_desired_count"),
        task_definition_args=FargateServiceTaskDefinitionArgs(
            cpu=_config.require("scheduler_task_cpu"),
            memory=_config.require("scheduler_task_memory"),
            task_role=DefaultRoleWithPolicyArgs(role_arn=task_role_arn),
            execution_role=DefaultRoleWithPolicyArgs(role_arn=task_role_arn),
            container=TaskDefinitionContainerDefinitionArgs(
                name="scheduler",
                image=create_image_name(
                    backend_repository_url, _config.require("version")
                ),
                essential=True,
                port_mappings=[
                    TaskDefinitionPortMappingArgs(
                        container_port=_config.require_int("scheduler_container_port"),
                    )
                ],
                command=_config.require_object("scheduler_container_command"),
                environment=_backend_environment,
                secrets=_backend_secrets,
            ),
        ),
    )


_backend_fargate_service = FargateService(
    "backend",
    cluster=cluster_arn,
    service_registries=ServiceServiceRegistriesArgs(
        registry_arn=backend_service_arn, container_name="backend"
    ),
    network_configuration=ServiceNetworkConfigurationArgs(
        subnets=network_private_subnet_ids,
        security_groups=[
            backend_security_group_id,
            database_access_security_group_id,
            cache_access_security_group_id,
        ],
    ),
    desired_count=_config.require_int("backend_service_desired_count"),
    task_definition_args=FargateServiceTaskDefinitionArgs(
        cpu=_config.require("backend_task_cpu"),
        memory=_config.require("backend_task_memory"),
        task_role=DefaultRoleWithPolicyArgs(role_arn=task_role_arn),
        execution_role=DefaultRoleWithPolicyArgs(role_arn=task_role_arn),
        container=TaskDefinitionContainerDefinitionArgs(
            name="backend",
            image=create_image_name(backend_repository_url, _config.require("version")),
            essential=True,
            port_mappings=[
                TaskDefinitionPortMappingArgs(
                    container_port=_config.require_int("backend_container_port"),
                )
            ],
            environment=_backend_environment,
            secrets=_backend_secrets,
        ),
    ),
    # FIXME: Add scheduler after turning it on
    opts=ResourceOptions(depends_on=[_worker_fargate_service]),
)

FargateService(
    "proxy",
    cluster=cluster_arn,
    service_registries=ServiceServiceRegistriesArgs(
        registry_arn=proxy_service_arn, container_name="proxy"
    ),
    network_configuration=ServiceNetworkConfigurationArgs(
        subnets=network_private_subnet_ids,
        security_groups=[
            proxy_security_group_id,
            frontend_access_security_group_id,
            backend_access_security_group_id,
        ],
    ),
    desired_count=_config.require_int("proxy_service_desired_count"),
    task_definition_args=FargateServiceTaskDefinitionArgs(
        cpu=_config.require("proxy_task_cpu"),
        memory=_config.require("proxy_task_memory"),
        task_role=DefaultRoleWithPolicyArgs(role_arn=task_role_arn),
        execution_role=DefaultRoleWithPolicyArgs(role_arn=task_role_arn),
        container=TaskDefinitionContainerDefinitionArgs(
            name="proxy",
            image=create_image_name(proxy_repository_url, _config.require("version")),
            essential=True,
            port_mappings=[TaskDefinitionPortMappingArgs(target_group=lb_target_group)],
            environment=[
                TaskDefinitionKeyValuePairArgs(
                    name="FRONTEND_UPSTREAM",
                    value=create_url_from_namespace(
                        frontend_service_name, private_dns_namespace_name
                    ),
                ),
                TaskDefinitionKeyValuePairArgs(
                    name="BACKEND_UPSTREAM",
                    value=create_url_from_namespace(
                        backend_service_name, private_dns_namespace_name
                    ),
                ),
            ],
        ),
    ),
    opts=ResourceOptions(
        depends_on=[_frontend_fargate_service, _backend_fargate_service]
    ),
)
