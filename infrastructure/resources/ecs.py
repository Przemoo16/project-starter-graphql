from helpers.string import (
    create_image_name,
    create_redis_url,
    create_token_url_template,
    create_upstream,
)
from modules.ecs import ECSService, ECSServiceArgs
from pulumi import Config, Input, ResourceOptions
from pulumi_aws.ecs import Cluster
from pulumi_aws.iam import (
    GetPolicyDocumentStatementArgs,
    GetPolicyDocumentStatementPrincipalArgs,
    ManagedPolicy,
    Policy,
    Role,
    RolePolicyAttachment,
    get_policy_document,
)
from pulumi_aws.servicediscovery import PrivateDnsNamespace
from pulumi_aws.ssm import Parameter

from resources.alb import dns_name, lb_target_group
from resources.ecr import (
    backend_repository_url,
    frontend_repository_url,
    proxy_repository_url,
)
from resources.elasticache import cache_endpoint
from resources.network import vpc_id, vpc_private_subnet_ids
from resources.rds import (
    database_host,
    database_name,
    database_password_parameter_name,
    database_port,
    database_username_parameter_name,
)

_config = Config()

_cluster = Cluster("ecs-cluster")

_private_dns_namespace = PrivateDnsNamespace("local", vpc=vpc_id)

_tasks_assume_role_policy_document = get_policy_document(
    statements=[
        GetPolicyDocumentStatementArgs(
            actions=["sts:AssumeRole"],
            principals=[
                GetPolicyDocumentStatementPrincipalArgs(
                    type="Service",
                    identifiers=["ecs-tasks.amazonaws.com"],
                )
            ],
        )
    ]
)
_secrets_access_policy_document = get_policy_document(
    statements=[
        GetPolicyDocumentStatementArgs(
            actions=["ssm:GetParameters"], resources=["*"], effect="Allow"
        )
    ]
)


_task_role = Role(
    "task-role", assume_role_policy=_tasks_assume_role_policy_document.json
)

_secrets_access_policy = Policy(
    "secrets-access-policy", policy=_secrets_access_policy_document.json
)

RolePolicyAttachment(
    "secrets-access-role-policy-attachment",
    policy_arn=_secrets_access_policy.arn,
    role=_task_role.name,
)

RolePolicyAttachment(
    "task-execution-role-policy-attachment",
    policy_arn=ManagedPolicy.AMAZON_ECS_TASK_EXECUTION_ROLE_POLICY,
    role=_task_role.name,
)

_frontend_service = ECSService(
    "frontend",
    ECSServiceArgs(
        cluster_arn=_cluster.arn,
        vpc_id=vpc_id,
        dns_namespace_id=_private_dns_namespace.id,
        subnet_ids=vpc_private_subnet_ids,
        service_desired_count=_config.require_int("frontend_service_desired_count"),
        task_cpu=_config.require("frontend_task_cpu"),
        task_memory=_config.require("frontend_task_memory"),
        task_role_arn=_task_role.arn,
        execution_role_arn=_task_role.arn,
        container_image=create_image_name(
            frontend_repository_url, _config.require("version")
        ),
        container_port=_config.require_int("frontend_container_port"),
    ),
)


_auth_private_key = Parameter(
    "auth_private_key",
    value=_config.require_secret("auth_private_key"),
    type="SecureString",
)
_smtp_user = Parameter(
    "smtp_user", value=_config.require_secret("smtp_user"), type="SecureString"
)
_smtp_password = Parameter(
    "smtp_password", value=_config.require_secret("smtp_password"), type="SecureString"
)

_backend_environment: dict[str, Input[str]] = {
    "DB__NAME": database_name,
    "DB__HOST": database_host,
    "DB__PORT": database_port.apply(str),
    "WORKER__BROKER_URL": create_redis_url(cache_endpoint),
    "WORKER__RESULT_BACKEND": create_redis_url(cache_endpoint),
    "USER__EMAIL_CONFIRMATION_URL_TEMPLATE": create_token_url_template(
        dns_name, "/confirm-email"
    ),
    "USER__RESET_PASSWORD_URL_TEMPLATE": create_token_url_template(
        dns_name, "/reset-password"
    ),
    "USER__AUTH_PUBLIC_KEY": _config.require("auth_public_key"),
    "EMAIL__SMTP_HOST": _config.require("smtp_host"),
    "EMAIL__SMTP_PORT": _config.require("smtp_port"),
    "EMAIL__SENDER": _config.require("email_sender"),
}

_backend_secrets = {
    "DB__USERNAME": database_username_parameter_name,
    "DB__PASSWORD": database_password_parameter_name,
    "USER__AUTH_PRIVATE_KEY": _auth_private_key.name,
    "EMAIL__SMTP_USER": _smtp_user.name,
    "EMAIL__SMTP_PASSWORD": _smtp_password.name,
}

_backend_service = ECSService(
    "backend",
    ECSServiceArgs(
        cluster_arn=_cluster.arn,
        vpc_id=vpc_id,
        dns_namespace_id=_private_dns_namespace.id,
        subnet_ids=vpc_private_subnet_ids,
        service_desired_count=_config.require_int("backend_service_desired_count"),
        task_cpu=_config.require("backend_task_cpu"),
        task_memory=_config.require("backend_task_memory"),
        task_role_arn=_task_role.arn,
        execution_role_arn=_task_role.arn,
        container_image=create_image_name(
            backend_repository_url, _config.require("version")
        ),
        container_port=_config.require_int("backend_container_port"),
        container_environment=_backend_environment,
        container_secrets=_backend_secrets,
    ),
)

ECSService(
    "proxy",
    ECSServiceArgs(
        cluster_arn=_cluster.arn,
        vpc_id=vpc_id,
        dns_namespace_id=_private_dns_namespace.id,
        subnet_ids=vpc_private_subnet_ids,
        service_desired_count=_config.require_int("proxy_service_desired_count"),
        task_cpu=_config.require("proxy_task_cpu"),
        task_memory=_config.require("proxy_task_memory"),
        task_role_arn=_task_role.arn,
        execution_role_arn=_task_role.arn,
        container_image=create_image_name(
            proxy_repository_url, _config.require("version")
        ),
        container_port=_config.require_int("proxy_container_port"),
        target_group=lb_target_group,
        container_environment={
            "FRONTEND_UPSTREAM": create_upstream(
                _frontend_service.service_discovery_name, _private_dns_namespace.name
            ),
            "BACKEND_UPSTREAM": create_upstream(
                _backend_service.service_discovery_name, _private_dns_namespace.name
            ),
        },
    ),
    opts=ResourceOptions(depends_on=[_frontend_service, _backend_service]),
)

ECSService(
    "worker",
    ECSServiceArgs(
        cluster_arn=_cluster.arn,
        vpc_id=vpc_id,
        dns_namespace_id=_private_dns_namespace.id,
        subnet_ids=vpc_private_subnet_ids,
        service_desired_count=_config.require_int("worker_service_desired_count"),
        task_cpu=_config.require("worker_task_cpu"),
        task_memory=_config.require("worker_task_memory"),
        task_role_arn=_task_role.arn,
        execution_role_arn=_task_role.arn,
        container_image=create_image_name(
            backend_repository_url, _config.require("version")
        ),
        container_port=_config.require_int("worker_container_port"),
        container_command=_config.require_object("worker_container_command"),
        container_environment=_backend_environment,
        container_secrets=_backend_secrets,
    ),
)

if _config.require_bool("scheduler_service_enabled"):
    ECSService(
        "scheduler",
        ECSServiceArgs(
            cluster_arn=_cluster.arn,
            vpc_id=vpc_id,
            dns_namespace_id=_private_dns_namespace.id,
            subnet_ids=vpc_private_subnet_ids,
            service_desired_count=_config.require_int(
                "scheduler_service_desired_count"
            ),
            task_cpu=_config.require("scheduler_task_cpu"),
            task_memory=_config.require("scheduler_task_memory"),
            task_role_arn=_task_role.arn,
            execution_role_arn=_task_role.arn,
            container_image=create_image_name(
                backend_repository_url, _config.require("version")
            ),
            container_port=_config.require_int("scheduler_container_port"),
            container_command=_config.require_object("scheduler_container_command"),
            container_environment=_backend_environment,
            container_secrets=_backend_secrets,
        ),
    )

private_dns_namespace_name = _private_dns_namespace.name
