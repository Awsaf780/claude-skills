# Review checklists

What to look for, by area. Every item came from a real review. They are examples, not the limit: the point is the pattern, in whatever stack the PR uses. Read only the sections the diff touches, plus Regressions and Craft every time.

## Regressions and blast radius

- **What merged since the branch was cut.** A shared helper, middleware, boundary or error mapper on the base can make the PR wrong without a conflict: a permissions boundary that now forbids the `sts:AssumeRole` the PR needs, a deleted `http.ts`, a new health Lambda that breaks "the first role" in a test.
- **What an open PR changes in the same place.** An alarm reading a metric with dimensions this PR doesn't emit; two PRs creating the same ADR number; one PR wrapping a client the other replaces. Say which PR must adapt when the other merges.
- **Behaviour that will change under the PR's feet.** A health check built on the app that is about to require a token returns 401 once auth lands, and the pipeline smoke test fails.
- **Deploy order.** A change that needs another stack or a hand-deployed baseline first, and nothing says so.
- **Plumbing connected everywhere.** A new parameter threaded through three of four callers; a rule enforced in the AI tool but not in the shared domain, so the actions API bypasses it.
- **Two sources for one fact.** The handler reads the theme id from one field, the picker from another, and they disagree for template-created charts.
- **Two copies of the same state** synced by a listener. Fix the structure: one copy, a selector over it, delete the other.
- **UI and backend disagree on a rule.** The UI disables Delete for one set of "defaults", the backend blocks a different set. One definition, used by both.
- **One field carrying two meanings.** `isDefault` used for "blocks delete" makes the UI say the wrong thing; return two facts.
- **Leftovers from testing.** A dev URL, a flipped `RETAIN` to `DESTROY`, a debug flag; often visible because a test now fails or the description says otherwise.
- **Description vs code.** What the description promises (protected data, unchanged URL, e2e passed) and what the diff does. An e2e spec "not run yet" must run before merge.
- **Coupled environments.** A build for dev that synthesizes or validates prod too fails on prod-only errors; let each pipeline build its own environment.

## Backend and API

- **Every error path ends in the API's error shape.** Errors that escape the handler (throttling, a network error, a config read that throws) reach the client as the gateway's generic 500, with nothing logged.
- **Map each SDK error the API can hit.** A single conditional `Put/Update/Delete` throws `ConditionalCheckFailedException`, not `TransactionCanceledException`; both mean 409, and an update still has to tell 404 from 409.
- **Routes the app never sees.** An HTTP API answers unknown paths and methods with its own 404 before the Lambda runs, so "every error is Problem Details" doesn't hold without a `$default` route.
- **Health checks.** Not behind auth; say how deep it checks. A dependency-free health Lambda only proves Lambda runs.
- **Body and payload limits** chosen from what they protect (Lambda's 6 MB invocation payload), not from an unrelated store limit.
- **Request id in logs**, from the gateway's id the client sees.
- **Config parsed once at cold start**, not per call, so a bad environment fails the deploy, not the first request.
- **Clients and pools created once per container**, not per tenant or per request; a per-tenant client means a TLS pool each and a map that grows without bound.
- **Every outbound call has a timeout.** An SDK client with no request timeout lets one hung call hold every request behind it until the Lambda times out.
- **Use what the SDK already does.** Credential caching and refresh (`fromTemporaryCredentials`) instead of a hand-written cache.
- **Independent awaits run together; started promises are all awaited.** Promises started together and awaited one by one leave the rest unhandled when an early one throws (`unhandledRejection`); use `Promise.all` or `allSettled` with a deliberate fallback.
- **Fail fast on a missing dependency** at boot, or have a health check that actually touches it; not neither.
- **No do-nothing abstractions** that every service now carries (a service-wide transaction wrapper that doesn't transact).
- **Validation rules defined once.** A stricter local rule than the shared schema turns valid sign-ins into 500s later; tighten the shared one and reuse it.
- **Names that shadow globals** (`Response`, `Request`, `Event`) confuse once `fetch` is used.
- **Events and messages are discriminated unions** by type, so clients can branch and new kinds don't break them.
- **An id checked as safe is checked at every sink** it reaches: a key, a path, a log line, a URL.
- **Log the caught `Error` itself**, not a copy of its name and message, so the stack and cause survive.
- **A failure window in front of a cache blocks only the network fetch**, never a read the cache can still answer.
- **Published response schemas stay open** (no `additionalProperties: false`); strict objects are for requests, since clients ignore unknown response fields (per the API ADR).
- **Spec values checked against the spec's own list before mapping onto a library enum**: CDK's `HttpMethod` lets `ANY` through.

## Data (DynamoDB, SQL, stores)

- **Pagination follows the store's continuation.** A DynamoDB `Query` returns at most 1 MB before filters; ignoring `LastEvaluatedKey` silently drops old items, and an in-memory filter misses matches past page one.
- **Cursors are opaque, signed, and bound to tenant and query**, since they carry internal keys.
- **Read-then-write races.** Reading a set, then updating related items in a separate write lets an add or remove slip in between; `UpdateItem` recreates a deleted item. Use conditions (`attribute_exists`) and fail if the set changed.
- **Limits stated but not enforced.** "About 90 references", "2000 entries": something must check them in the write path.
- **Shared helpers that overwrite fields.** A per-write `version` bump overwrites a field that stores another entity's version; use a separate attribute.
- **Writes into something being deleted** leave orphans; condition on the parent existing.
- **Transaction limits** (100 items) cap bulk operations; say what happens past them.
- **Key design serves the listing.** A filter on a non-key attribute gives near-empty pages; put the discriminator in the sort key.
- **Item size** that can grow toward 400 KB; split it. **Hot partitions.** **No `Scan`.**
- **Existence leaks through counts.** A count larger than the visible list tells the user hidden items exist.
- **Removal policy on data.** `DESTROY` on tables and buckets without `autoDeleteObjects` gets the stack stuck half-deleted, and loses data nobody meant to lose.
- **Generated models regenerated, not hand-edited**; compare the shape against a sibling the generator produced.

## Frontend

- **One store, one copy.** Derived data comes from a selector over the single source, not a second slice kept in sync.
- **Every state handled**: loading, empty, error, disabled. A failed catalog or chunk load must not leave a blank app; fall back (e.g. to the default locale).
- **Design system first.** Use the shared component and tokens; no colour or size literals; follow the primitive library's composition pattern so components stay consistent.
- **The UI package doesn't bundle app-level dependencies** (the router); a wrapper that loses the router's type-safe props is a regression.
- **Showcases and dev pages live outside the product app**, so they don't leak into route types or the bundle.
- **Right-to-left.** Logical properties (`start`, `ms-`), and anything centred with a translate needs the RTL flip (`rtl:translate-x-1/2`), or it lands a full width off.
- **Accessibility**: accessible names, keyboard path, visible focus, contrast from the token values, errors in text and linked with `aria-describedby`.
- **Splitting packages by runtime.** Generic code in one entry, Lambda-only or Node-only code in another, and check the unused part really stays out of the bundle.
- **Route edge cases.** `/render` without the slash, dotted path segments, trailing slashes, query strings and HEAD on a health route.

## Security

- **Authorization in the code that acts**, before any side effect; identity from the verified token only, never a header, path or body.
- **Tenant isolation**: a test with another tenant's valid token that gets nothing back; keys that start with the tenant; nothing that sets the tenant outside the token.
- **Dev-only shortcuts enforced in code**, not by "we only deploy it to dev". An anonymous context that every enabled environment would get is a hole.
- **Not found and not allowed answer the same**, so a caller can't learn what exists.
- **Untrusted HTML never runs on the app origin**; sandboxed iframe without `allow-same-origin`, or a separate domain.
- **Token claims that copy a registry** go stale; keep only the id in the token.
- **Security metrics that can tell attack from outage.** A "boundary denied" metric that also counts STS throttling, with the reason not a dimension, makes the alarm useless.
- **Hand-written auth, crypto, token, parsing or retry code** where a maintained library does it.
- **Secrets** in plain env vars, templates or logs; personal data in logs without retention.

## AWS and CDK

- **Permissions boundaries scoped to what is assumed.** A boundary allowing `sts:AssumeRole` on `cdk-*` or `${prefix}*` lets any role reach the lookup role (ReadOnlyAccess, which is tenant data) and the asset bucket. Allow the exact roles, and test that the lookup role can't be assumed. A name prefix that also matches pipeline roles is too broad; use an IAM path.
- **`iam:PassRole` scoped** to one role and to the services that environment actually has.
- **Trust policies and `s3:*`.** IAM can't condition on trust-policy contents; `s3:*` includes `PutBucketPolicy` and `DeletePublicAccessBlock`. Account-level Block Public Access in the baseline.
- **SCPs apply to admins too.** A "deny delete" SCP blocks `cdk destroy` and the rollback of a failed first deploy (`ROLLBACK_FAILED`).
- **Globally unique names.** S3 bucket names built from a stack name without the account collide across accounts; user-supplied names (a developer's) can equal a shared cell's. Derive the reserved list from config, not a hard-coded value.
- **Config that promises what the guardrails can't do** (a cell in another account): throw until it's built, or drop the option, and fix the comment, README and ADR.
- **Compile-time over runtime.** An invalid prop combination (`autoDeleteObjects` with `RETAIN`) as a discriminated union.
- **Synth-time checks** that need build output break `cdk ls`, `synth` and `diff` for every stack; check only when the stack is selected.
- **Assets.** `exclude` on the deployment only still zips and uploads everything as a second asset; put it on the source. `prune: false` with nothing ever cleaning up grows forever.
- **CloudFront and S3 for a SPA.** A "has a dot, so it's a file" rule breaks `/users/jane.doe`; OAC without `s3:ListBucket` turns missing objects into 403 XML.
- **Duplicated hardening settings** between constructs drift; share them.
- **Distinguishable resources.** Two distributions with the same comment, two alarms with the same name.
- **Region-bound services.** CloudFront certificates and log delivery setup live in `us-east-1`; that means bootstrap, baseline and pipeline changes or a custom resource.
- **IAM policy size** (6,144 characters for managed policies) when a policy grows.
- **Throttling, reserved concurrency and access logs** on a public API stage.
- **CloudWatch metrics match dimension sets exactly.** An alarm on `{cell}` never sees a metric emitted with `{tenantId, cell, service}`.
- **STS `RoleSessionName`** is at most 64 characters; truncating makes two tenants look the same in CloudTrail.
- **Logical IDs that depend on order** (an integration named after its first route) get replaced when the order changes; pin them in a test.
- **Gateway protections on the API default**, not per route, when routes come from a spec.
- **Cold start** from heavy imports (undici via fetch, zod locales, source maps); measure before optimizing.

## CI and supply chain

- **No `curl | bash` and no `@latest` in a build** that produces what gets deployed. Pin through the package manager and its lockfile; add a test that fails on `@latest`.
- **Actions pinned to a commit SHA**, with only the permissions they need; no `pull_request_target` that runs the PR's code.
- **CI and the pipeline run the same script**; only the install step differs.
- **Notification and reminder logic**: use the platform's own event times (push activity), not commit dates; force pushes rewrite history; idempotency keys must not move backwards; ignore drafts, closed PRs, failing checks.
- **The write token on the one step that uses it**, with PR code in a read-only job; job-level `env` hands it to every step.
- **Diffing two checkouts**: each side installs its own dependencies, or a bump shows on neither; asset hashes are masked only where they sit.
- **CI scripts that report**: failure state per producer, and every returned error reaches an output; an error excerpt keeps the start, where the message is; a fallback after a missing artifact says the job did not run, not that the PR failed.
- **New dependencies**: maintainer, usage, name near-misses, install scripts, and whether a smaller existing one does it.

## Tests

- **A test that passes when the tool never ran.** "Exit code isn't 0" passes when the command can't start; assert the expected rule name or output.
- **Portability**: spawning a tool by name without a shell fails on Windows; CRLF line endings; `/` vs `\` in expected paths.
- **Tests that find things by position** ("the first role") break when a sibling is added; look up by name.
- **Mocks restored** between tests; prefer the global `restoreMocks` setting.
- **Tests that test the mock**, not the component.
- **Skipped or weakened tests** without a linked ticket.
- **Tests that stop checking without failing**: parse-then-assert once a schema strips extra fields; a time window tested only at its edges, so send one request mid-way; bad-input fixtures derived from whichever real config matches, instead of fixed data.
- **Test-only inputs on deployed code**: a prop, env var or option only tests use belongs on a pure function.
- **Missing test for the risky path**, especially the cross-tenant case, the API path that bypasses the UI, and the round trip (save, reopen, still there).

## Craft and conventions

- **Comments are rare and stand alone.** No comments that restate the code, describe a caller, mention the agent session or "previous code", or need the PR to make sense.
- **Enforce with the linter, not with docs.** A rule a linter can check belongs in lint config, not in AGENTS.md or a harness check.
- **No new conventions slipped in** through agent instructions or harness rules without the team agreeing.
- **No duplicated constants kept in sync by a test**; read the value from its source.
- **Docs that copy config go stale**: a README table of accounts and branches; point at the config.
- **Dead code and entry points** that contradict the docs (a `cdk` script the README says not to use).
- **Unused imports, workarounds for a broken local setup** (fix the setup), ignore-file entries instead of fixing the cause.
- **Consistent names** for the same idea (`durationMin/Max`, not `durationMs` beside `duration`).
- **A new standards rule applies to the existing cases** in the files the change touches, not only to the new code.
- **Generators and converters that fall back silently** (a schema converter that publishes `{}` for `unknown`) need a guard that throws.
- **Build only what's needed**: no option or layer nobody asked for; no premature helper.

## Docs and ADRs

- **Contradictions between ADRs, and between an ADR and the code or another open PR.** Say which one wins if the team already decided.
- **Ambiguous words that decide behaviour**: "change" (does it include adding?), "visible to" (orgs or groups?), terms nobody defined.
- **Stated limits and guarantees with nothing enforcing them.**
- **Security consequences an ADR should name**: existence leaks, cross-org rendering, who can do what with a read-only share.
- **Reasons recorded**, not just the decision.
- **Scope.** On an ADR, implementation details (exact endpoints, consumers, intervals) are usually left for the build; raise them as questions or follow-ups, not as blockers.
- **Status and numbering**: "Proposed" vs "Accepted", and number collisions with other open PRs.
