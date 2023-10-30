# Infrastructure

## TODO Improvements

- Refactor all security groups ingress to restrict access by specifying concrete
  security groups that should have access to the resource instead of allowing all
  inbound traffic (cidr_blocks=["0.0.0.0/0"]). Consider if this is necessary as all
  resources are in a private subnets and only load balancer is accessible from the
  internet.
- Restructure the project so it is easier to pass different resources like having
  a generic ECS security group that is passed as ingress to database or cache.
- Use the `role-to-assume` feature when pushing images to ECR instead of AWS secrets
  (as done in the infrastructure-preview job).
