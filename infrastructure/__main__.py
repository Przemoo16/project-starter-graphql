import pulumi
import pulumi_aws as aws
from helpers.string import (
    create_image_name,
    create_redis_url,
    create_token_url_template,
    create_upstream,
)
from modules.ecs import (
    ECSService,
    ECSServiceArgs,
    create_ecs_cluster,
    create_private_dns_namespace,
    get_ecs_tasks_assume_role_policy_document,
    get_secrets_access_policy_document,
)
from modules.iam import create_policy, create_role, create_role_policy_attachment
from pulumi_aws.ssm import Parameter
from resources.alb import dns_name, lb_target_group
from resources.ecr import (
    backend_repository_url,
    frontend_repository_url,
    proxy_repository_url,
)
from resources.elasticache import cache_endpoint
from resources.network import vpc_id, vpc_private_subnet_ids, vpc_public_subnet_ids
from resources.rds import (
    database_endpoint,
    database_host,
    database_name,
    database_password_parameter_name,
    database_port,
    database_username_parameter_name,
)

config = pulumi.Config()

cluster = create_ecs_cluster("ecs-cluster")

private_dns_namespace = create_private_dns_namespace("local", vpc_id)

tasks_assume_role_policy_document = get_ecs_tasks_assume_role_policy_document()
secrets_access_policy_document = get_secrets_access_policy_document()

task_role = create_role("task-role", tasks_assume_role_policy_document.json)

secrets_access_policy = create_policy(
    "secrets-access-policy", secrets_access_policy_document.json
)

create_role_policy_attachment(
    "secrets-access-role-policy-attachment", task_role.name, secrets_access_policy.arn
)

create_role_policy_attachment(
    "task-execution-role-policy-attachment",
    task_role.name,
    aws.iam.ManagedPolicy.AMAZON_ECS_TASK_EXECUTION_ROLE_POLICY,
)

frontend_service = ECSService(
    "frontend",
    ECSServiceArgs(
        cluster_arn=cluster.arn,
        vpc_id=vpc_id,
        dns_namespace_id=private_dns_namespace.id,
        subnet_ids=vpc_private_subnet_ids,
        service_desired_count=config.require_int("frontend_service_desired_count"),
        task_cpu=config.require("frontend_task_cpu"),
        task_memory=config.require("frontend_task_memory"),
        task_role_arn=task_role.arn,
        execution_role_arn=task_role.arn,
        container_image=create_image_name(
            frontend_repository_url, config.require("version")
        ),
        container_port=config.require_int("frontend_container_port"),
    ),
)


auth_private_key = Parameter(
    "auth_private_key",
    value=config.require_secret("auth_private_key"),
    type="SecureString",
)
smtp_user = Parameter(
    "smtp_user", value=config.require_secret("smtp_user"), type="SecureString"
)
smtp_password = Parameter(
    "smtp_password", value=config.require_secret("smtp_password"), type="SecureString"
)

backend_environment: dict[str, pulumi.Input[str]] = {
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
    "USER__AUTH_PUBLIC_KEY": config.require("auth_public_key"),
    "EMAIL__SMTP_HOST": config.require("smtp_host"),
    "EMAIL__SMTP_PORT": config.require("smtp_port"),
    "EMAIL__SENDER": config.require("email_sender"),
}

backend_secrets = {
    "DB__USERNAME": database_username_parameter_name,
    "DB__PASSWORD": database_password_parameter_name,
    "USER__AUTH_PRIVATE_KEY": auth_private_key.name,
    "EMAIL__SMTP_USER": smtp_user.name,
    "EMAIL__SMTP_PASSWORD": smtp_password.name,
}

backend_service = ECSService(
    "backend",
    ECSServiceArgs(
        cluster_arn=cluster.arn,
        vpc_id=vpc_id,
        dns_namespace_id=private_dns_namespace.id,
        subnet_ids=vpc_private_subnet_ids,
        service_desired_count=config.require_int("backend_service_desired_count"),
        task_cpu=config.require("backend_task_cpu"),
        task_memory=config.require("backend_task_memory"),
        task_role_arn=task_role.arn,
        execution_role_arn=task_role.arn,
        container_image=create_image_name(
            backend_repository_url, config.require("version")
        ),
        container_port=config.require_int("backend_container_port"),
        container_environment=backend_environment,
        container_secrets=backend_secrets,
    ),
)

proxy_environment = {
    "FRONTEND_UPSTREAM": create_upstream(
        frontend_service.service_discovery_name, private_dns_namespace.name
    ),
    "BACKEND_UPSTREAM": create_upstream(
        backend_service.service_discovery_name, private_dns_namespace.name
    ),
}

proxy_service = ECSService(
    "proxy",
    ECSServiceArgs(
        cluster_arn=cluster.arn,
        vpc_id=vpc_id,
        dns_namespace_id=private_dns_namespace.id,
        subnet_ids=vpc_private_subnet_ids,
        service_desired_count=config.require_int("proxy_service_desired_count"),
        task_cpu=config.require("proxy_task_cpu"),
        task_memory=config.require("proxy_task_memory"),
        task_role_arn=task_role.arn,
        execution_role_arn=task_role.arn,
        container_image=create_image_name(
            proxy_repository_url, config.require("version")
        ),
        container_port=config.require_int("proxy_container_port"),
        target_group=lb_target_group,
        container_environment=proxy_environment,
    ),
    opts=pulumi.ResourceOptions(depends_on=[frontend_service, backend_service]),
)

ECSService(
    "worker",
    ECSServiceArgs(
        cluster_arn=cluster.arn,
        vpc_id=vpc_id,
        dns_namespace_id=private_dns_namespace.id,
        subnet_ids=vpc_private_subnet_ids,
        service_desired_count=config.require_int("worker_service_desired_count"),
        task_cpu=config.require("worker_task_cpu"),
        task_memory=config.require("worker_task_memory"),
        task_role_arn=task_role.arn,
        execution_role_arn=task_role.arn,
        container_image=create_image_name(
            backend_repository_url, config.require("version")
        ),
        container_port=config.require_int("worker_container_port"),
        container_command=config.require_object("worker_container_command"),
        container_environment=backend_environment,
        container_secrets=backend_secrets,
    ),
)

if config.require_bool("scheduler_service_enabled"):
    ECSService(
        "scheduler",
        ECSServiceArgs(
            cluster_arn=cluster.arn,
            vpc_id=vpc_id,
            dns_namespace_id=private_dns_namespace.id,
            subnet_ids=vpc_private_subnet_ids,
            service_desired_count=config.require_int("scheduler_service_desired_count"),
            task_cpu=config.require("scheduler_task_cpu"),
            task_memory=config.require("scheduler_task_memory"),
            task_role_arn=task_role.arn,
            execution_role_arn=task_role.arn,
            container_image=create_image_name(
                backend_repository_url, config.require("version")
            ),
            container_port=config.require_int("scheduler_container_port"),
            container_command=config.require_object("scheduler_container_command"),
            container_environment=backend_environment,
            container_secrets=backend_secrets,
        ),
    )

pulumi.export("frontend_repository_url", frontend_repository_url)
pulumi.export("backend_repository_url", backend_repository_url)
pulumi.export("proxy_repository_url", proxy_repository_url)

pulumi.export("vpc_id", vpc_id)
pulumi.export("private_subnets_ids", vpc_private_subnet_ids)
pulumi.export("public_subnets_ids", vpc_public_subnet_ids)

pulumi.export("private_dns_namespace_name", private_dns_namespace.name)

pulumi.export("database_endpoint", database_endpoint)

pulumi.export("cache_endpoint", cache_endpoint)

pulumi.export("lb_dns_name", dns_name)

pulumi.export("ecs_cluster_name", cluster.name)
pulumi.export("ecs_cluster_arn", cluster.arn)
