import pulumi
import pulumi_aws as aws

cluster = aws.ecs.Cluster("ecs-cluster")

pulumi.export("ecs_cluster_name", cluster.name)
pulumi.export("ecs_cluster_arn", cluster.arn)
