import pulumi
from helpers.date import get_utc_timestamp
from helpers.hash import generate_hash
from helpers.string import create_image_name, create_redis_url
from modules.alb import ALB, ALBArgs
from modules.ecr import create_ecr_repository
from modules.ecs import ECSService, ECSServiceArgs, create_ecs_cluster
from modules.elasticache import ElastiCache, ElastiCacheArgs
from modules.network import create_vpc
from modules.rds import RDS, RDSArgs

project = pulumi.get_project()
stack = pulumi.get_stack()
config = pulumi.Config()

frontend_repository = create_ecr_repository(config.require("frontend_repository_name"))
backend_repository = create_ecr_repository(config.require("backend_repository_name"))

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
    "frontend-lb",
    ALBArgs(
        vpc_id=vpc.vpc_id,
        target_port=config.require_int("frontend_container_port"),
        subnet_ids=vpc.public_subnet_ids,
    ),
)

cluster = create_ecs_cluster("ecs-cluster")

frontend_service = ECSService(
    "frontend",
    ECSServiceArgs(
        cluster_arn=cluster.arn,
        vpc_id=vpc.vpc_id,
        subnet_ids=vpc.private_subnet_ids,
        service_desired_count=config.require_int("frontend_service_desired_count"),
        task_cpu=config.require("frontend_task_cpu"),
        task_memory=config.require("frontend_task_memory"),
        container_image=create_image_name(
            frontend_repository.url, config.require("frontend_image_tag")
        ),
        container_port=config.require_int("frontend_container_port"),
        target_group=lb.target_group,
    ),
)

backend_environment = {
    "DB__PASSWORD": config.require_secret("database_password"),
    "DB__USERNAME": database.username,
    "DB__NAME": database.name,
    "DB__HOST": database.host,
    "DB__PORT": database.port.apply(str),
    "CELERY__BROKER_URL": create_redis_url(cache.endpoint),
    "CELERY__RESULT_BACKEND": create_redis_url(cache.endpoint),
}

backend_service = ECSService(
    "backend",
    ECSServiceArgs(
        cluster_arn=cluster.arn,
        vpc_id=vpc.vpc_id,
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

celery_worker_service = ECSService(
    "celery-worker",
    ECSServiceArgs(
        cluster_arn=cluster.arn,
        vpc_id=vpc.vpc_id,
        subnet_ids=vpc.private_subnet_ids,
        service_desired_count=config.require_int("celery_worker_service_desired_count"),
        task_cpu=config.require("celery_worker_task_cpu"),
        task_memory=config.require("celery_worker_task_memory"),
        container_image=create_image_name(
            backend_repository.url, config.require("backend_image_tag")
        ),
        container_port=config.require_int("celery_worker_container_port"),
        container_command=config.require_object("celery_worker_container_command"),
        container_environment=backend_environment,
    ),
)

celery_beat_service = ECSService(
    "celery-beat",
    ECSServiceArgs(
        cluster_arn=cluster.arn,
        vpc_id=vpc.vpc_id,
        subnet_ids=vpc.private_subnet_ids,
        service_desired_count=config.require_int("celery_beat_service_desired_count"),
        task_cpu=config.require("celery_beat_task_cpu"),
        task_memory=config.require("celery_beat_task_memory"),
        container_image=create_image_name(
            backend_repository.url, config.require("backend_image_tag")
        ),
        container_port=config.require_int("celery_beat_container_port"),
        container_command=config.require_object("celery_beat_container_command"),
        container_environment=backend_environment,
    ),
)

pulumi.export("frontend_repository_url", frontend_repository.url)
pulumi.export("backend_repository_url", backend_repository.url)

pulumi.export("vpc_id", vpc.vpc_id)
pulumi.export("private_subnets_ids", vpc.private_subnet_ids)
pulumi.export("public_subnets_ids", vpc.public_subnet_ids)

pulumi.export("database_endpoint", database.endpoint)

pulumi.export("cache_endpoint", cache.endpoint)

pulumi.export("lb_dns_name", lb.dns_name)

pulumi.export("ecs_cluster_name", cluster.name)
pulumi.export("ecs_cluster_arn", cluster.arn)
