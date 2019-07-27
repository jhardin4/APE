# APE_GUI

## Coding style

### Pre-Commit
The Docker container comes with [pre-commit](https://pre-commit.com/) installed.
pre-commit is a pre-commit framework which can be attached as git hook. It
runs code-formatting and other checks automatically before committing any code.
You just need to install with:

```bash
pre-commit install
pre-commit autoupdate
```

### Python

For Python we can use [black](https://github.com/ambv/black):

```bash
black -S .
```

**NOTE:** The `-S` parameter prevents black from changing quotes.
