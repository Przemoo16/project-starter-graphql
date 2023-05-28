import pulumi
from modules.alb import ALB, ALBArgs
from modules.date import get_utc_timestamp
from modules.ecs import ECSService, ECSServiceArgs, create_ecs_cluster
from modules.hash import generate_hash
from modules.network import create_vpc
from modules.rds import RDS, RDSArgs

config = pulumi.Config()

vpc = create_vpc("vpc")

database = RDS(
    "database",
    RDSArgs(
        vpc_id=vpc.vpc_id,
        subnet_ids=vpc.private_subnet_ids,
        port=config.require_int("database_port"),
        name=config.require("database_name"),
        engine=config.require("database_engine"),
        engine_version=config.require("database_engine_version"),
        storage_type=config.require("database_storage_type"),
        allocated_storage=config.require_int("database_allocated_storage"),
        instance_class=config.require("database_instance_class"),
        final_snapshot_identifier=(
            "project-starter-graphql-"
            f"{generate_hash(get_utc_timestamp(), digest_size=16)}"
        ),
        username=config.require("database_username"),
        password=config.require_secret("database_password"),
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
        container_image=config.require("frontend_container_image"),
        container_port=config.require_int("frontend_container_port"),
        target_group=lb.target_group,
    ),
)

# TODO: Pass DB envs to the container
backend_service = ECSService(
    "backend",
    ECSServiceArgs(
        cluster_arn=cluster.arn,
        vpc_id=vpc.vpc_id,
        subnet_ids=vpc.private_subnet_ids,
        service_desired_count=config.require_int("backend_service_desired_count"),
        task_cpu=config.require("backend_task_cpu"),
        task_memory=config.require("backend_task_memory"),
        container_image=config.require("backend_container_image"),
        container_port=config.require_int("backend_container_port"),
    ),
)


pulumi.export("vpc_id", vpc.vpc_id)
pulumi.export("private_subnets_ids", vpc.private_subnet_ids)
pulumi.export("public_subnets_ids", vpc.public_subnet_ids)

pulumi.export("database_endpoint", database.endpoint)

pulumi.export("lb_dns_name", lb.dns_name)

pulumi.export("ecs_cluster_name", cluster.name)
pulumi.export("ecs_cluster_arn", cluster.arn)
