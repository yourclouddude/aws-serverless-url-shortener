# Troubleshooting

Common problems learners may hit while running this project.

## `TABLE_NAME environment variable is required`

The Lambda code expects the table name from the SAM template.

When running handlers manually, set a local value first:

```bash
export TABLE_NAME=your-table-name
```

On Windows PowerShell:

```powershell
$env:TABLE_NAME="your-table-name"
```

For normal AWS deployments, SAM injects this automatically.

## `sam: command not found`

Install the AWS SAM CLI, then confirm:

```bash
sam --version
```

Restart your terminal if the installer updated your PATH.

## `sam validate --lint` fails

Check these first:

1. Your SAM CLI is current enough for the template runtime.
2. YAML indentation has not been changed accidentally.
3. You are running the command from the repository root.

Then run:

```bash
sam validate --lint --debug
```

Use the debug output to identify the exact resource or property causing the failure.

## Deployment returns an IAM authorization error

Your AWS identity must be allowed to create the resources used by the CloudFormation stack, including Lambda, API Gateway, DynamoDB, IAM roles, and CloudFormation resources.

Do not solve this by putting administrator credentials in the repository. Use an approved AWS account/profile with the permissions required by your environment.

## Short link returns `404`

Possible reasons:

- the short code does not exist
- you are calling a different deployment/Region
- the item was removed
- you copied the code incorrectly

Check the DynamoDB table for the partition key shown in the creation response.

## Short link returns `410`

`410 Gone` means the record exists but has passed its application expiration time. This is expected even if the expired DynamoDB item is still visible temporarily because TTL deletion is asynchronous.

## Tests attempt to contact AWS

The unit tests should use fake table objects and should not require an AWS account. If a new test calls the real `get_table()` helper, replace it with a test double using `monkeypatch`.

## `ruff` reports formatting or import problems

Run:

```bash
python -m ruff check src tests
```

For automatically fixable issues:

```bash
python -m ruff check src tests --fix
```

Review the resulting diff before committing.

## How to debug a failed Lambda after deployment

Start with CloudWatch logs for the failing function, then check:

1. request payload shape
2. environment variables
3. IAM authorization errors
4. DynamoDB table name and Region
5. exception type and request ID

Avoid logging secrets, credentials, authorization tokens, or sensitive destination data unnecessarily.

## Clean up after learning

To avoid leaving billable resources running:

```bash
sam delete
```

Then confirm the CloudFormation stack and related resources are gone in the AWS console.
