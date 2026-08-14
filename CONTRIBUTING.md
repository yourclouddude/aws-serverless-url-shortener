# Contributing

Thanks for improving this YourCloudDude learner project.

## Good contributions

Contributions should make the project easier to understand, safer to run, or more useful for learning. Examples:

- clearer explanations or troubleshooting
- additional tests for realistic failure cases
- observability improvements
- optional learner extensions with documented trade-offs
- accessibility or clarity improvements in examples

Avoid adding services only to make the architecture look more complex.

## Development checks

Before opening a pull request, run:

```bash
pip install -r requirements-dev.txt
python -m ruff check src tests
python -m pytest -q
sam validate --lint
sam build
```

## Security

Never commit:

- AWS access keys or secret keys
- session tokens
- `.env` files containing credentials
- private certificates
- production endpoints containing sensitive information
- learner/customer data

If you believe you found a security issue, do not publish credentials or exploit details in a public issue. Contact YourCloudDude privately through the website instead.

## Pull requests

Keep pull requests focused. Explain:

1. what problem you are solving
2. what changed
3. how you tested it
4. any AWS cost, security, or architecture implications

The project favors understandable engineering decisions over unnecessary complexity.
