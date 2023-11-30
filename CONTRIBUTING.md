# Contributing to mf2py 🛠️

Thank you for your interest in contributing to mf2py! In this document, we outline all you need to know to submit a contribution to the mf2py project.

## Contribution Guidelines

We welcome contributions to:

1. Add new parsing features to the library (see *Adding Parsing Features* below for more information).
2. Improve documentation.
3. Report bugs and issues.
4. Submit a request for a new feature.
5. Add more test cases.

We encourage you to submit an Issue to discuss any new feature requests before submitting a PR.

### Adding Parsing Features

As the official `mf2py` parser, we will only implement new parsing features after they have been ratified into the Microformats parsing standard, or have achieved sufficient support among contributors to parsing discussions and requires implementations. The [microformats2 parsing](https://github.com/microformats/microformats2-parsing/issues) repository is the offical home to all issues pertaining to microformats2 parsing.

## How to Contribute Changes

First, fork this repository to your own GitHub account. Create a new branch that describes your changes (i.e. `line-counter-docs`). Push your changes to the branch on your fork and then submit a pull request to this repository.

When creating new functions, please ensure you have the following:

1. Docstrings for the function and all parameters.
2. Unit tests for the function.
3. Examples in the documentation for any public functions.
4. Created an entry in our docs to autogenerate the documentation for the function, if the function is public.

All pull requests will be reviewed by the maintainers of the project. We will provide feedback and ask for changes if necessary.

PRs must pass all tests and linting requirements before they can be merged.

## Code Quality

Before you submit a PR to `mf2py`, run the following command in the base directory of the project:

```bash
make lint
```

This will format your code using the linters configured with the project.

## Tests

Before you submit a PR, please run the `mf2py` test suite on your code. You can do so using the following command:

```bash
make test
```

## Join the Microformats Community

Have a question about microformats or mf2py? Join the `#microformats` disussion on Slack, Discord, or IRC. Guidance on how to join the community is available on the [IndieWeb wiki](https://indieweb.org/discuss).
