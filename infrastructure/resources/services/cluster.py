from pulumi_aws.ecs import Cluster

_cluster = Cluster("ecs-cluster")

cluster_arn = _cluster.arn
