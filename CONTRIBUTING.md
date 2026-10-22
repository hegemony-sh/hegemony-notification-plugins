<!--
SPDX-FileCopyrightText: 2025-2026 Rexonix s.r.o.
SPDX-FileContributor: Jakub Trávník <jakub.travnik@gmail.com>

SPDX-License-Identifier: AGPL-3.0-or-later
-->

# Contributing

This repository holds the notification SDK and plugin wheels of
[Hegemony](https://github.com/hegemony-sh/hegemony). The
[README](README.md) says what is in it and how to write a notification plugin.
Keep contributions small, tested, and tied to a concrete issue.

## Code of Conduct and security

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).

Report vulnerabilities privately through the process in
[SECURITY.md](SECURITY.md). Do **not** open public issues for vulnerabilities,
leaked secrets, exploit details, or suspected compromise.

## Licensing and DCO

This repository is part of the Hegemony project. Its source is licensed under
`AGPL-3.0-or-later`. See [LICENSE](LICENSE) and [LICENSING.md](LICENSING.md).
Your contribution is licensed under the same terms, and
contributing it transfers no copyright to the project. There is no Contributor
License Agreement.

The project's own files name Rexonix s.r.o. as the copyright holder and Jakub
Trávník as the author (see [LICENSING.md](LICENSING.md)). If you do not write
on behalf of Rexonix s.r.o., you keep the copyright in your contribution and
may add your own `SPDX-FileCopyrightText` line to the header of a file you
change, as REUSE recommends.

Every commit must be signed off under the
[Developer Certificate of Origin](https://developercertificate.org/) (DCO),
version 1.1. A `Signed-off-by:` line certifies that you wrote the change, or
otherwise have the right to submit it under the project licence. Sign off with
`git commit -s`. The DCO GitHub App checks every commit in a pull request: the
sign-off's name and email must match the commit's author. Merge
commits and commits by GitHub bot accounts are skipped. To add a missing
sign-off to every commit on your branch, run
`git rebase --signoff origin/main` and force-push the branch.

A commit written by an AI coding agent is signed off by the person who directs
the agent and submits the work, as its author; the agent is credited in a
`Co-authored-by:` trailer and never signs off in its own name. See the
platform's
[CONTRIBUTING.md](https://github.com/hegemony-sh/hegemony/blob/develop/CONTRIBUTING.md#licensing-and-dco).

Licensing questions: [contact@hegemony.sh](mailto:contact@hegemony.sh).

## Setting up and checking a change

Install the workspace and the git hooks with [uv](https://docs.astral.sh/uv/):

```bash
uv sync --all-packages
uv run pre-commit install --install-hooks
```

Before you open a pull request, run what CI runs. `task ci` runs the same list
when [Task](https://taskfile.dev/) is installed:

```bash
uv run ruff check packages plugins tests scripts
uv run ruff format --check packages plugins tests scripts
uv run reuse lint
uv run ty check
uv run pytest
uv run python scripts/build_wheels.py
uv run python scripts/smoke_install_wheels.py
```

`uv run pre-commit run --all-files` runs every hook, which adds the typo check,
the workflow scan (zizmor), the secret scan (gitleaks) and commitlint. CI runs
the last three on every pull request as well.

Every file carries an SPDX header: a copyright line and the licence
identifier `AGPL-3.0-or-later`. `reuse lint` fails without one. Copy the header
of a neighbouring file. A file that cannot hold a comment is annotated in
`REUSE.toml`.

A first-party file names Rexonix s.r.o. as the copyright holder and Jakub
Trávník as the author, in the file's own comment syntax:

<!-- REUSE-IgnoreStart -->

```python
# SPDX-FileCopyrightText: 2025-2026 Rexonix s.r.o.
# SPDX-FileContributor: Jakub Trávník <jakub.travnik@gmail.com>
#
# SPDX-License-Identifier: AGPL-3.0-or-later
```

<!-- REUSE-IgnoreEnd -->

## Pull requests and commit messages

Open pull requests against `main`. Commit messages follow
[Conventional Commits](https://www.conventionalcommits.org/), and commitlint
(`commitlint.config.mjs`) checks every commit of a pull request. The scope is
optional: lower-case letters, digits and single dashes, at most 20 characters,
for example `fix(core-transports): ...` or `docs: ...`.

A merge to `main` is a release, and the commit type decides whether there is
one, so choose it for what the change does to the published wheels; the table
under [Releasing](#releasing) lists the rules. A change to a plugin's behaviour
is `fix` or `feat`. Documentation, CI and test changes are `docs`, `ci` and
`test`, and release nothing.

Notification transports handle SMTP, webhook and Shoutrrr URLs. Tests and
documentation use example hosts (`example.com`, `example.org`, or a subdomain
of them) and synthetic credentials, never a real address, hostname, token or
webhook URL, even one that no longer works.

## Releasing

A merge to `main` is a release. The `Release` workflow calls the shared
[`plugin-release.yml`](https://github.com/hegemony-sh/hegemony-github-workflows)
workflow, which runs [semantic-release](https://semantic-release.gitbook.io/):
it reads the Conventional Commits since the last tag, derives the next
version from them, bumps every package and SDK pin (`scripts/set_version.py`),
refreshes `uv.lock`, builds and smoke-installs the wheels, prepends
`CHANGELOG.md`, commits `chore(release): X.Y.Z [skip ci]`, tags `vX.Y.Z` and
publishes the wheels plus `SHA256SUMS` as the GitHub Release. There is no
manual step any more: do not bump versions or push `v*` tags by hand.

| Commits since the last tag | Release |
|---|---|
| `fix`, `perf`, `revert` | patch |
| `feat` | minor |
| breaking change (`feat!:`, `fix!:` or a `BREAKING CHANGE:` footer) | **minor, while the major is 0** |
| `chore`, `docs`, `ci`, `test`, `refactor`, `build`, `style` | none |

The 0.x rule is the `"breaking": true` entry in `.releaserc.json`'s
`releaseRules`; once the packages reach 1.0, change its `release` to
`major`. Deleting it is not enough: the rules are tried in order and the
first match wins, so a breaking `feat` would still match the `feat` rule and
release a minor.

Releases are immutable. The pipeline refuses to run when a GitHub Release for
the next tag already exists and never replaces published assets: fix forward
with a new commit, which becomes the next release. The shared workflow creates
a build-provenance attestation for the wheels and `SHA256SUMS` only while the
repository is public, because GitHub attestations need a public repository (or
an Enterprise plan). The releases cut so far, up to `v0.3.0`, were cut while
the repository was private and ship checksums only.

One failure a re-run cannot repair: semantic-release pushes the release
commit and the `vX.Y.Z` tag before it publishes the GitHub Release, so if
publication fails after that push the tag exists without a Release, and the
next run reads the tag as the last release. Publish that tag's assets by hand
from a checkout of the tag, as the shared workflow's
[README](https://github.com/hegemony-sh/hegemony-github-workflows#recovering-a-tag-without-a-release)
describes (`gh release create vX.Y.Z --verify-tag ... dist/*.whl
dist/SHA256SUMS` after rebuilding the wheels at that tag).

The shared workflow is pinned by commit in `.github/workflows/release.yml`;
a change merged to it reaches this repository through a pull request that
bumps that SHA.
