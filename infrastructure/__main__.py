import pulumi
import pulumi_aws as aws
from helpers.date import get_utc_timestamp
from helpers.hash import generate_hash
from helpers.string import (
    create_image_name,
    create_redis_url,
    create_token_url_template,
    create_upstream,
)
from modules.alb import ALB, ALBArgs
from modules.ecs import (
    ECSService,
    ECSServiceArgs,
    create_ecs_cluster,
    create_private_dns_namespace,
    get_ecs_tasks_assume_role_policy_document,
    get_secrets_access_policy_document,
)
from modules.iam import create_policy, create_role, create_role_policy_attachment
from modules.rds import RDS, RDSArgs
from modules.ssm import create_ssm_parameter
from resources.ecr import backend_repository, frontend_repository, proxy_repository
from resources.elasticache import cache
from resources.network import vpc

project = pulumi.get_project()
stack = pulumi.get_stack()
config = pulumi.Config()


database = RDS(
    "database",
    RDSArgs(
        vpc_id=vpc.vpc_id,
        subnet_ids=vpc.private_subnet_ids,
        name=config.require("database_name"),
        port=config.require_int("database_port"),
        engine=config.require("database_engine"),
        engine_version=config.require("database_engine_version"),
        storage_type=config.require("database_storage_type"),
        allocated_storage=config.require_int("database_allocated_storage"),
        instance_class=config.require("database_instance_class"),
        final_snapshot_identifier=(
            f"{project}-{generate_hash(get_utc_timestamp(), digest_size=16)}"
        ),
        username=config.require_secret("database_username"),
        password=config.require_secret("database_password"),
    ),
)

lb = ALB(
    "lb",
    ALBArgs(
        vpc_id=vpc.vpc_id,
        target_port=config.require_int("proxy_container_port"),
        subnet_ids=vpc.public_subnet_ids,
        health_check_path=config.require("proxy_health_check_path"),
    ),
)

cluster = create_ecs_cluster("ecs-cluster")

private_dns_namespace = create_private_dns_namespace("local", vpc.vpc_id)

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
        vpc_id=vpc.vpc_id,
        dns_namespace_id=private_dns_namespace.id,
        subnet_ids=vpc.private_subnet_ids,
        service_desired_count=config.require_int("frontend_service_desired_count"),
        task_cpu=config.require("frontend_task_cpu"),
        task_memory=config.require("frontend_task_memory"),
        task_role_arn=task_role.arn,
        execution_role_arn=task_role.arn,
        container_image=create_image_name(
            frontend_repository.url, config.require("version")
        ),
        container_port=config.require_int("frontend_container_port"),
    ),
)

database_username = create_ssm_parameter(
    "database_username", config.require_secret("database_username"), "SecureString"
)
database_password = create_ssm_parameter(
    "database_password", config.require_secret("database_password"), "SecureString"
)
auth_private_key = create_ssm_parameter(
    "auth_private_key", config.require_secret("auth_private_key"), "SecureString"
)
smtp_user = create_ssm_parameter(
    "smtp_user", config.require_secret("smtp_user"), "SecureString"
)
smtp_password = create_ssm_parameter(
    "smtp_password", config.require_secret("smtp_password"), "SecureString"
)

backend_environment: dict[str, pulumi.Input[str]] = {
    "DB__NAME": database.name,
    "DB__HOST": database.host,
    "DB__PORT": database.port.apply(str),
    "WORKER__BROKER_URL": create_redis_url(cache.primary_endpoint_address),
    "WORKER__RESULT_BACKEND": create_redis_url(cache.primary_endpoint_address),
    "USER__EMAIL_CONFIRMATION_URL_TEMPLATE": create_token_url_template(
        lb.dns_name, "/confirm-email"
    ),
    "USER__RESET_PASSWORD_URL_TEMPLATE": create_token_url_template(
        lb.dns_name, "/reset-password"
    ),
    "USER__AUTH_PUBLIC_KEY": config.require("auth_public_key"),
    "EMAIL__SMTP_HOST": config.require("smtp_host"),
    "EMAIL__SMTP_PORT": config.require("smtp_port"),
    "EMAIL__SENDER": config.require("email_sender"),
}

backend_secrets = {
    "DB__USERNAME": database_username.name,
    "DB__PASSWORD": database_password.name,
    "USER__AUTH_PRIVATE_KEY": auth_private_key.name,
    "EMAIL__SMTP_USER": smtp_user.name,
    "EMAIL__SMTP_PASSWORD": smtp_password.name,
}

backend_service = ECSService(
    "backend",
    ECSServiceArgs(
        cluster_arn=cluster.arn,
        vpc_id=vpc.vpc_id,
        dns_namespace_id=private_dns_namespace.id,
        subnet_ids=vpc.private_subnet_ids,
        service_desired_count=config.require_int("backend_service_desired_count"),
        task_cpu=config.require("backend_task_cpu"),
        task_memory=config.require("backend_task_memory"),
        task_role_arn=task_role.arn,
        execution_role_arn=task_role.arn,
        container_image=create_image_name(
            backend_repository.url, config.require("version")
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
        vpc_id=vpc.vpc_id,
        dns_namespace_id=private_dns_namespace.id,
        subnet_ids=vpc.private_subnet_ids,
        service_desired_count=config.require_int("proxy_service_desired_count"),
        task_cpu=config.require("proxy_task_cpu"),
        task_memory=config.require("proxy_task_memory"),
        task_role_arn=task_role.arn,
        execution_role_arn=task_role.arn,
        container_image=create_image_name(
            proxy_repository.url, config.require("version")
        ),
        container_port=config.require_int("proxy_container_port"),
        target_group=lb.target_group,
        container_environment=proxy_environment,
    ),
    opts=pulumi.ResourceOptions(depends_on=[frontend_service, backend_service]),
)

ECSService(
    "worker",
    ECSServiceArgs(
        cluster_arn=cluster.arn,
        vpc_id=vpc.vpc_id,
        dns_namespace_id=private_dns_namespace.id,
        subnet_ids=vpc.private_subnet_ids,
        service_desired_count=config.require_int("worker_service_desired_count"),
        task_cpu=config.require("worker_task_cpu"),
        task_memory=config.require("worker_task_memory"),
        task_role_arn=task_role.arn,
        execution_role_arn=task_role.arn,
        container_image=create_image_name(
            backend_repository.url, config.require("version")
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
            vpc_id=vpc.vpc_id,
            dns_namespace_id=private_dns_namespace.id,
            subnet_ids=vpc.private_subnet_ids,
            service_desired_count=config.require_int("scheduler_service_desired_count"),
            task_cpu=config.require("scheduler_task_cpu"),
            task_memory=config.require("scheduler_task_memory"),
            task_role_arn=task_role.arn,
            execution_role_arn=task_role.arn,
            container_image=create_image_name(
                backend_repository.url, config.require("version")
            ),
            container_port=config.require_int("scheduler_container_port"),
            container_command=config.require_object("scheduler_container_command"),
            container_environment=backend_environment,
            container_secrets=backend_secrets,
        ),
    )

pulumi.export("frontend_repository_url", frontend_repository.url)
pulumi.export("backend_repository_url", backend_repository.url)
pulumi.export("proxy_repository_url", proxy_repository.url)

pulumi.export("vpc_id", vpc.vpc_id)
pulumi.export("private_subnets_ids", vpc.private_subnet_ids)
pulumi.export("public_subnets_ids", vpc.public_subnet_ids)

pulumi.export("private_dns_namespace_name", private_dns_namespace.name)

pulumi.export("database_endpoint", database.endpoint)

pulumi.export("cache_endpoint", cache.primary_endpoint_address)

pulumi.export("lb_dns_name", lb.dns_name)

pulumi.export("ecs_cluster_name", cluster.name)
pulumi.export("ecs_cluster_arn", cluster.arn)
