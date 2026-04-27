# Contributing

Thanks for your interest in contributing. Bug reports, new skills, fixes, and
documentation improvements are all welcome.

## Reporting bugs or requesting features

Please use the GitHub issue tracker. Before opening a new issue, check
existing open and recently closed issues to avoid duplicates. Helpful issues
usually include:

- A minimal reproduction or step-by-step scenario
- The version of the code (commit SHA or release tag)
- Relevant local modifications
- Anything unusual about your environment or deployment

## Pull requests

1. Work against the latest `main`.
2. Check open and recently merged PRs to avoid duplicate effort. For
   non-trivial changes, open an issue first to agree on direction.
3. Fork, branch, and keep the diff focused on one change — avoid bundling
   unrelated reformatting.
4. Run any local tests or validation steps relevant to your change.
5. Open the PR with a clear description and respond to CI feedback.

## Contributing a new skill

The skill spec (frontmatter, directory layout, heading conventions) lives
in **[AGENTS.md](./AGENTS.md)**. The quick-start is in the
[README](./README.md#author-a-skill). Before opening a PR, verify:

- [ ] `SKILL.md` frontmatter is valid YAML
- [ ] `name` matches the directory name (kebab-case)
- [ ] `description` reads as trigger phrases, not a flat summary
- [ ] Section headings match the template in AGENTS.md
- [ ] All referenced files (`references/*`, `scripts/*`) exist
- [ ] `SKILL.md` stays under ~500 lines (push detail into `references/`)

## Finding something to work on

Issues labeled `help wanted` or `good first issue` are a good starting
point.

## Security issues

**Do not open public issues for security vulnerabilities.** Report them via
the [AWS vulnerability reporting page](http://aws.amazon.com/security/vulnerability-reporting/).

## Code of conduct

This project follows the
[Amazon Open Source Code of Conduct](https://aws.github.io/code-of-conduct).
See the [Code of Conduct FAQ](https://aws.github.io/code-of-conduct-faq) or
email opensource-codeofconduct@amazon.com for questions.

## Licensing

See [LICENSE](./LICENSE). We will ask you to confirm the licensing of your
contribution as part of the PR.
