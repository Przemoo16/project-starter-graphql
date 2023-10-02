import pulumi
from helpers.date import get_utc_timestamp
from helpers.hash import generate_hash
from helpers.string import (
    create_image_name,
    create_redis_url,
    create_token_url_template,
)
from modules.alb import ALB, ALBArgs
from modules.ecr import create_ecr_repository
from modules.ecs import (
    ECSService,
    ECSServiceArgs,
    create_ecs_cluster,
    create_private_dns_namespace,
)
from modules.elasticache import ElastiCache, ElastiCacheArgs
from modules.network import create_vpc
from modules.rds import RDS, RDSArgs

project = pulumi.get_project()
stack = pulumi.get_stack()
config = pulumi.Config()

frontend_repository = create_ecr_repository(config.require("frontend_repository_name"))
backend_repository = create_ecr_repository(config.require("backend_repository_name"))
proxy_repository = create_ecr_repository(config.require("proxy_repository_name"))

vpc = create_vpc("vpc")


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
        username=config.require("database_username"),
        password=config.require_secret("database_password"),
    ),
)

cache = ElastiCache(
    "cache",
    ElastiCacheArgs(
        vpc_id=vpc.vpc_id,
        subnet_ids=vpc.private_subnet_ids,
        port=config.require_int("cache_port"),
        description=(f"Redis cache for the {stack!r} stack in the {project!r} project"),
        engine_version=config.require("cache_engine_version"),
        node_type=config.require("cache_node_type"),
    ),
)

lb = ALB(
    "lb",
    ALBArgs(
        vpc_id=vpc.vpc_id,
        target_port=config.require_int("proxy_container_port"),
        subnet_ids=vpc.public_subnet_ids,
    ),
)

cluster = create_ecs_cluster("ecs-cluster")

private_dns_namespace = create_private_dns_namespace("local", vpc.vpc_id)

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
        container_image=create_image_name(
            frontend_repository.url, config.require("frontend_image_tag")
        ),
        container_port=config.require_int("frontend_container_port"),
    ),
)

backend_environment: dict[str, pulumi.Input[str]] = {
    "DB__PASSWORD": config.require_secret("database_password"),
    "DB__USERNAME": database.username,
    "DB__NAME": database.name,
    "DB__HOST": database.host,
    "DB__PORT": database.port.apply(str),
    "CELERY__BROKER_URL": create_redis_url(cache.endpoint),
    "CELERY__RESULT_BACKEND": create_redis_url(cache.endpoint),
    "USER__EMAIL_CONFIRMATION_URL_TEMPLATE": create_token_url_template(
        lb.dns_name, "/confirm-email"
    ),
    "USER__RESET_PASSWORD_URL_TEMPLATE": create_token_url_template(
        lb.dns_name, "/reset-password"
    ),
    "USER__AUTH_PRIVATE_KEY": config.require_secret("auth_private_key"),
    "USER__AUTH_PUBLIC_KEY": config.require("auth_public_key"),
    "EMAIL__SMTP_HOST": config.require("smtp_host"),
    "EMAIL__SMTP_PORT": config.require("smtp_port"),
    "EMAIL__SMTP_USER": config.require("smtp_user"),
    "EMAIL__SMTP_PASSWORD": config.require_secret("smtp_password"),
    "EMAIL__SENDER": config.require("email_sender"),
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
        container_image=create_image_name(
            backend_repository.url, config.require("backend_image_tag")
        ),
        container_port=config.require_int("backend_container_port"),
        container_environment=backend_environment,
    ),
)

ECSService(
    "proxy",
    ECSServiceArgs(
        cluster_arn=cluster.arn,
        vpc_id=vpc.vpc_id,
        dns_namespace_id=private_dns_namespace.id,
        subnet_ids=vpc.private_subnet_ids,
        service_desired_count=config.require_int("proxy_service_desired_count"),
        task_cpu=config.require("proxy_task_cpu"),
        task_memory=config.require("proxy_task_memory"),
        container_image=create_image_name(
            proxy_repository.url, config.require("proxy_image_tag")
        ),
        container_port=config.require_int("proxy_container_port"),
        target_group=lb.target_group,
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
        container_image=create_image_name(
            backend_repository.url, config.require("backend_image_tag")
        ),
        container_port=config.require_int("worker_container_port"),
        container_command=config.require_object("worker_container_command"),
        container_environment=backend_environment,
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
            container_image=create_image_name(
                backend_repository.url, config.require("backend_image_tag")
            ),
            container_port=config.require_int("scheduler_container_port"),
            container_command=config.require_object("scheduler_container_command"),
            container_environment=backend_environment,
        ),
    )

pulumi.export("frontend_repository_url", frontend_repository.url)
pulumi.export("backend_repository_url", backend_repository.url)
pulumi.export("proxy_repository_url", proxy_repository.url)

pulumi.export("vpc_id", vpc.vpc_id)
pulumi.export("private_subnets_ids", vpc.private_subnet_ids)
pulumi.export("public_subnets_ids", vpc.public_subnet_ids)

pulumi.export("private_dns_namespace_id", private_dns_namespace.id)

pulumi.export("database_endpoint", database.endpoint)

pulumi.export("cache_endpoint", cache.endpoint)

pulumi.export("lb_dns_name", lb.dns_name)

pulumi.export("ecs_cluster_name", cluster.name)
pulumi.export("ecs_cluster_arn", cluster.arn)
