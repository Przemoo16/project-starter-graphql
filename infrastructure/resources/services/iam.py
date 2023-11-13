from pulumi_aws.iam import (
    GetPolicyDocumentStatementArgs,
    GetPolicyDocumentStatementPrincipalArgs,
    ManagedPolicy,
    Policy,
    Role,
    RolePolicyAttachment,
    get_policy_document,
)

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

task_role_arn = _task_role.arn
