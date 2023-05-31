# Infrastructure

## TODO Improvements

- Use the SSM Parameter to save the database password and pass it as a container
  secret instead of passing it as environment variable.
- Refactor all security groups ingress to restrict access by specifying concrete
  security groups that should have access to the resource instead of allowing all
  inbound traffic (cidr_blocks=["0.0.0.0/0"]).
- Restructure the project so it is easier to pass different resources like having
  a generic ECS security group that is passed as ingress to database or cache.
