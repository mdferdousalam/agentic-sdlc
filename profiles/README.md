# Profiles — the opinions that are not universal

The pipeline core is stack-agnostic on purpose. A profile is where a *kind* of project's
standards live, applied only when `"profile"` in `sdlc.config.json` names it.

This separation is deliberate. A rule like "no hardcoded value that the spec marked
configurable" is right for an admin-driven web application and meaningless for a compiler.
Baking it into the core would make the core lie about being stack-agnostic, and would make
every reviewer on every other kind of project produce noise.

| Profile | For | Adds |
| --- | --- | --- |
| `webapp` | product applications with an admin surface | configurability, data model, accessibility, migration safety |
| `library` | published packages and SDKs | public API compatibility, semver, documentation of every exported symbol |
| `service` | long-running network services | operability, failure modes, observability, backpressure |
| `compiler` | language and toolchain projects | specification-first, evidence vocabulary, bounded heavy workloads |

Write your own: a profile is one markdown file of standards the reviewers and the spec reviewer
read in addition to the core rules. Keep it to what a reviewer can check.
