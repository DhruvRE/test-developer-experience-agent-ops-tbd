# Team Workstreams

Three owners, one product. Each owner has a clear area, a task list, and a definition of done.

| Person | Area |
|---|---|
| **Yogesh** | GitHub integration and the CI views in the app |
| **Ishan** | Test suites, the test repo, the eval harness, and the fix validator |
| **Dhruv** | Agent ops (AI error detection, fixing, automated pull requests) and monitoring support |

Goal for the first 8 weeks: a failed GitHub Actions run is detected, diagnosed, and (when it is a code or config problem)
turned into a validated fix pull request that a human approves. Targets and the 20-failure evaluation set are in `docs/product/PLAN.md`.

---

## 1. Who owns what

| | Yogesh | Ishan | Dhruv |
|---|---|---|---|
| Mission | Link repos to projects. Show every CI run, step, log, and failure | Prove it works: tests, test repo, scoring, validation | Detect, diagnose, fix, and open PRs with AI. Add monitoring |
| Backend code | `apps/api/src/modules/{auth,github,projects,webhooks,runs}` | `apps/eval`, `packages/validator`, `packages/testing` | `apps/worker/src/{failures,agent}`, `apps/api/src/modules/{agent,monitoring}` |
| Frontend code | `apps/web/src/features/{auth,projects,runs,failures}` | none | `apps/web/src/features/{agent,monitoring}` |
| Other | GitHub App, webhooks | `failure-testbed` repo, `ci.yml` of the main repo | Prompts, agent traces, metrics |
| Database tables | `User`, `Organization`, `Project`, `Run`, `Job`, `Step`, `Failure` | none (reads only) | `Diagnosis`, `AgentRun`, `FixAttempt` |

**Dhruv has the largest scope**, so the plan protects his time:
- Prometheus, Grafana, and custom widgets start only after the week 8 decision. Until then, monitoring means platform metrics and agent traces (section 6).
- Ishan builds the fix validator (sandbox), not Dhruv.
- Yogesh builds the PR-writing primitive in the GitHub client. Dhruv's agent calls it.
- Yogesh builds the failure pages and approval screens. Dhruv supplies the diagnosis and fix panels that sit inside them.

### Pipeline views versus monitoring (no overlap)
- **Yogesh, pipeline views:** data that comes from GitHub: runs, jobs, steps, durations, status, logs, failures, success rate and average duration per project.
- **Dhruv, monitoring:** data the platform and agents produce: agent success rate, classification accuracy, cost and latency, queue health. Later: Prometheus/Grafana integration, the Metrics Gateway, custom widgets, alerting.

---

## 2. Contracts between you (agree in week 1, half a day together)

Define each as a Zod schema in `packages/shared`. Do not change one without telling the others first.

| Contract | From → To | Content |
|---|---|---|
| `FailureDetected` job | Yogesh → Dhruv | `failureId`, `projectId`, `repoFullName`, `runId`, `headSha`, `branch`, `workflowName` |
| `GitHubClient` service | Yogesh → Dhruv | `getFailedJobLogs(failureId)`, `getFileContents(repo, path, ref)`, `listRecentCommits(repo, ref)`, `createPullRequest({ repo, baseSha, branchName, patch, title, body })` |
| Diagnosis API and `DiagnosisPanel` | Dhruv → Yogesh | `GET /api/failures/:id/diagnosis` (class, reason, confidence, proposed patch, validation, PR link) and a React component Yogesh embeds in the failure detail page |
| `FixProposal` object | within Dhruv's agent | `failureId`, `classification`, `outcome` (`fix` / `diagnosis` / `retry`), `patch`, `explanation`, `confidence` |
| `validatePatch()` | Ishan → Dhruv | Input: `repo`, `sha`, `patch`. Output: pass/fail per step and a short summary |
| Testbed `meta.json` | Ishan → Dhruv | `id`, `slug`, `class`, `expectedOutcome`, `description`, `expectedFiles` |
| Eval result row | Ishan → all | `failureId`, `classifiedCorrectly`, `outcomeCorrect`, `validationPassed`, `wouldMerge`, `secretLeak`, `minutes` |

**Database changes:** Yogesh owns the first migration (users, projects, runs, failures). Dhruv adds his tables in separate migrations. Pull `main` right before creating any migration.

---

## 3. Weekly milestones

| Week | Yogesh | Ishan | Dhruv | Checkpoint |
|---|---|---|---|---|
| 1 | GitHub App, login with GitHub | Create `failure-testbed`, healthy app, unit tests, workflow green on `main` | Collect first logs from the testbed, build log cleaner and redactor | Contracts agreed. Testbed is green on `main` and red on a failure branch |
| 2 | Connect repo → project, webhook endpoint, `Run`/`Job`/`Step`/`Failure` tables | Integration and smoke tests, failure branches 1-10, main repo CI | Classifier v1 on collected logs | Break a testbed branch → the failure appears in the app |
| 3 | Runs list, run detail (jobs, steps, durations), log viewer | Failure branches 11-20, eval harness v1 (classification only) | Classifier accuracy report, diagnosis API, `DiagnosisPanel` | First eval run: classification accuracy |
| 4-5 | `createPullRequest` in the GitHub client, failures list and detail pages | Fix validator (sandbox) | Context builder, fix agent, agent traces | A fix PR is opened for an easy failure |
| 6-7 | Approve / reject / request-change, audit log, project overview stats | Eval harness v2 (full scoring), test coverage in CI | Fix panel with validation result, platform metrics | Full flow works for 3 failures |
| 8 | Demo prep | Final run of all 20 failures | Prompt and context fixes for the worst cases | Decide together: continue, change approach, or narrow |

Targets at week 8: classification ≥ 80%, validated fix PRs ≥ 30% of rows 1-17, zero secret leaks.

---

## 4. Working agreements

- Follow `AGENTS.md` and the skills in `.claude/skills/`. One task, one task file in `tasks/`, one branch, one PR.
- Run `pnpm tasks:list` at the start of each day and check overlaps before starting.
- Every change goes through a PR. A teammate reviews. Rebase on `main` first.
- Change a contract only after posting it in the team chat, in its own small PR.
- Short sync (15 minutes): done, next, blocked.

---

## 5. Yogesh: GitHub integration and CI views

**Goal:** anyone can link a GitHub repo to a project and then see all CI runs, steps, logs, and failures for it in the app.

### Step 1. Create the GitHub App (everyone depends on this)
- [ ] GitHub organization → Settings → Developer settings → GitHub Apps → New GitHub App.
- [ ] Webhook URL: tunnel URL + `/api/webhooks/github`. Generate a webhook secret.
- [ ] Repository permissions: **Contents** read and write, **Pull requests** read and write, **Actions** read, **Metadata** read.
- [ ] Subscribe to events: **Workflow run** and **Workflow job**.
- [ ] Enable user authorization (OAuth) during installation. Set the callback URL to the API.
- [ ] Generate a private key. Never commit it. Put the App ID, client ID, client secret, webhook secret, and key in `.env` and placeholders in `.env.example`.
- [ ] Set up a stable tunnel (Cloudflare Tunnel or ngrok). Document it in `docs/guides/github-app-setup.md`.

### Step 2. Login with GitHub
- [ ] `modules/auth`: GitHub OAuth, session or JWT, `GET /api/auth/me`.
- [ ] Store users (GitHub id, login, avatar). Never store tokens in plain text.
- [ ] Web: login button, callback, header with the user name.
- [ ] Tests: login, logout, 401 when logged out.

### Step 3. Link repos to projects
- [ ] Store the installation id per organization.
- [ ] `GitHubModule` with Octokit and GitHub App authentication (short-lived installation tokens).
- [ ] `GET /api/github/repos` lists repos available to the installation.
- [ ] `POST /api/projects` saves a chosen repo as a project.
- [ ] Web: "Connect repo" page and project list page.
- [ ] On connect, backfill the last 20 workflow runs so the project is not empty.

### Step 4. Webhooks
- [ ] `POST /api/webhooks/github`: use the raw body, verify `X-Hub-Signature-256` (HMAC SHA-256), reject invalid signatures with 401.
- [ ] Handle `workflow_run` and `workflow_job` events. Upsert `Run`, `Job`, and `Step` rows with status, conclusion, start and end times.
- [ ] When a run completes with `conclusion = failure`, create a `Failure` row and enqueue `FailureDetected`.
- [ ] De-duplicate with `X-GitHub-Delivery` and run id, so a redelivered webhook changes nothing.
- [ ] Tests: valid and invalid signature, duplicate delivery, out-of-order events, non-failure events.

### Step 5. GitHub client (for Dhruv, by end of week 3)
- [ ] `getFailedJobLogs(failureId)`: find failed jobs of the run, download job logs, return text per job and step.
- [ ] `getFileContents` and `listRecentCommits`.
- [ ] `createPullRequest`: create a branch from `baseSha`, apply the patch, commit, open a PR. Never push to the default branch.
- [ ] Handle rate limits and 404s with clear errors. Test with a fake client and once against the testbed repo.

### Step 6. CI views in the web app
- [ ] **Project overview:** latest runs, success rate, average duration, failure count.
- [ ] **Runs list:** filter by branch, workflow, status.
- [ ] **Run detail:** jobs and steps as a timeline with status and duration.
- [ ] **Log viewer:** per step, collapsible, searchable, fetched on demand and cached.
- [ ] **Failures list and detail:** run info, redacted log excerpt, and Dhruv's `DiagnosisPanel` embedded.

### Step 7. Approval and audit (weeks 6-7)
- [ ] Approve, reject, and request-change on a fix attempt, stored with who and when.
- [ ] Audit log entry for each AI action and each human decision.

### Definition of done
Break a testbed branch → the run, steps, logs, and failure appear in the app within seconds, and (later) the fix PR is linked on the failure page.

---

## 6. Dhruv: agent ops and monitoring support

**Goal:** turn a raw failure into a safe diagnosis and, when appropriate, a validated fix PR. Make every agent action visible and measurable.

### Part A. Failure intelligence (weeks 1-3)

**A1. Collect real logs first (week 1)**
- [ ] Take the first failing testbed branches from Ishan, download their logs, and store fake-data fixtures in `apps/worker/test/fixtures/logs/`.

**A2. Log cleanup**
- [ ] `log-cleaner`: strip ANSI codes and timestamps, keep the failing step, extract error lines plus context, enforce a maximum size. Tests with fixtures.

**A3. Redaction (must exist before any text reaches a model)**
- [ ] `redactor`: GitHub tokens, AWS keys, private key blocks, JWTs, bearer tokens, `KEY=value` secrets, emails, IP addresses.
- [ ] Tests for each pattern, and a test that fails if any known fake secret in the fixtures survives.
- [ ] The AI client accepts only a `RedactedText` type, so unredacted text cannot be sent by mistake.

**A4. Classifier**
- [ ] Worker processor for `FailureDetected`: fetch logs via `GitHubClient`, clean, redact, classify.
- [ ] Classes: `code`, `dependency`, `config`, `infra`, `secrets`, `flaky`. Structured output validated by Zod, with a reason and confidence.
- [ ] Store a `Diagnosis`. Expose `GET /api/failures/:id/diagnosis` and the `DiagnosisPanel` component.
- [ ] Measure accuracy against Ishan's `meta.json`. **Target ≥ 80% before building the fix agent.**

### Part B. Fix agent and automated pull requests (weeks 4-7)

- [ ] **Context builder:** failing files named in the log, recent commits, config files (Dockerfile, workflow, manifests). No secret values.
- [ ] **Fix agent:** returns a `FixProposal`. For `infra`, `secrets`, and `flaky` it must return `diagnosis` or `retry` guidance and no patch.
- [ ] **Guardrails:** the agent only produces patches and never executes anything. Limit patch size and number of files. Never edit secret files or workflow permissions. Skip below a confidence threshold.
- [ ] **Validation:** send each patch to Ishan's `validatePatch()`. Open a PR only if it passes. Otherwise store the attempt with the reason.
- [ ] **PR creation:** call Yogesh's `createPullRequest` with a description containing classification, explanation, redacted log excerpt, and validation result.
- [ ] **Fix panel:** show the patch, validation result, and PR link inside the failure detail page.

### Part C. Agent ops (build alongside Part B)
- [ ] **Traces:** an `AgentRun` record for every attempt: failure, prompt version, model, context files used, tokens, cost, latency, outcome.
- [ ] **Prompt versions:** prompts live in the repo as files with a version number. Every `AgentRun` stores which version produced it.
- [ ] **Replay:** re-run an attempt from its stored redacted inputs, so you can test a prompt change against past failures.
- [ ] **Limits:** per-project daily cost and attempt caps, with a clear message when reached.
- [ ] **Human loop:** every PR waits for human approval. The agent never merges.

### Part D. Monitoring support
**Now (weeks 5-7): platform metrics**
- [ ] Add Prometheus-format metrics (`prom-client`) to the API and worker: failures detected, classification results, fix attempts by outcome, validation pass rate, queue depth, job duration, agent cost.
- [ ] A simple Monitoring page in the web app showing these numbers.

**After the week 8 decision**
- [ ] Prometheus and Grafana provisioning through IaC with the approval loop, the Metrics Gateway, custom widgets, and the Alerting tab (see `docs/architecture/`).

### Definition of done
A failed run produces a stored, redacted, correctly classified diagnosis in the dashboard. For fixable failures it opens a validated PR. Every agent attempt has a trace, and no secrets reach any model input.

---

## 7. Ishan: tests, test repo, eval, and validation

**Goal:** a trustworthy way to measure the product, plus a test repo with realistic tests that the platform links to as a customer project.

### Part A. Create the testing repo (`failure-testbed`)

Why a separate repo: the GitHub App needs real repos with real Actions runs, and intentional failures must not pollute the product repo.

**A1. Create and protect the repo**
- [ ] In your GitHub organization: New repository → `failure-testbed`.
- [ ] Public is fine (fake sample code only, no secrets) and avoids using private Actions minutes.
- [ ] Add a README and a Node `.gitignore`.
- [ ] Settings → Branches: protect `main` (PR required). Leave `fail/**` branches unprotected.
- [ ] Add teammates and install Yogesh's GitHub App on this repo.

**A2. Structure**
```bash
git clone git@github.com:<org>/failure-testbed.git
cd failure-testbed
mkdir -p app/src app/test/{unit,integration,e2e} app/k8s failures scripts .github/workflows
```
```
failure-testbed/
├─ app/                          # small healthy Node + TypeScript API with Postgres
│  ├─ src/                       # index.ts, routes/health.ts, routes/items.ts, math.ts
│  ├─ test/
│  │  ├─ unit/                   # pure logic
│  │  ├─ integration/            # API + real Postgres
│  │  └─ e2e/                    # smoke test against the built container
│  ├─ k8s/                       # deployment.yaml, service.yaml
│  ├─ Dockerfile
│  └─ package.json, tsconfig.json
├─ .github/workflows/ci-deploy.yml
├─ failures/                     # NN-slug/{patch.diff, meta.json}
├─ scripts/                      # create-branches.sh, verify-patches.sh, reset-branches.sh
└─ README.md
```

**A3. Baseline app and test suites (all must pass on `main`)**
- [ ] App: Express + TypeScript, `GET /health`, CRUD on `/items` stored in Postgres, a few pure functions in `math.ts`.
- [ ] **Unit tests** (`test/unit`): pure functions and validation logic, no I/O. Use the same runner as the main repo.
- [ ] **Integration tests** (`test/integration`): `supertest` against the app with a real Postgres (service container in CI, Docker locally). Cover create, read, update, delete, and error cases.
- [ ] **End-to-end smoke tests** (`test/e2e`): start the built container, call `/health` and `/items`, check responses.
- [ ] **Static checks:** lint and typecheck.
- [ ] Scripts in `package.json`: `lint`, `typecheck`, `test:unit`, `test:integration`, `test:e2e`, `build`.
- [ ] `Dockerfile` that builds and starts the app on a fixed port, and Kubernetes manifests with a readiness probe on `/health`.

**A4. Workflow (`ci-deploy.yml`)**
Triggers: push to `main` and `fail/**`. Use separate jobs so each failure shows up in a distinct job and step, which also gives Yogesh's step views realistic data:
1. `static`: install, lint, typecheck
2. `unit`: unit tests
3. `integration`: integration tests with a Postgres service container
4. `build-and-smoke`: build, `docker build`, start the container, run e2e smoke tests
5. `manifests`: validate the Kubernetes manifests (for example with kubeconform)

No real cluster is needed. The smoke test and manifest validation stand in for a deployment.

**A5. Verify the baseline**
- [ ] Push to `main` and confirm every job is green before creating any failures.

**A6. Create the failures**
The 20 failures from `docs/product/PLAN.md`. Make sure they cover every test type: at least one unit test failure (for example an assertion broken by a signature change), one integration failure (wrong database environment variable), one e2e smoke failure (wrong port), and one flaky test.
- [ ] For each: branch from `main`, make exactly one change, confirm the workflow goes red for the intended reason.
- [ ] Save it: `git diff main > failures/NN-slug/patch.diff`.
- [ ] Write `failures/NN-slug/meta.json`:
```json
{
  "id": "01",
  "slug": "typo-import",
  "class": "code",
  "expectedOutcome": "fix",
  "description": "Import path has a typo in src/index.ts",
  "expectedFiles": ["app/src/index.ts"]
}
```
- [ ] Ideas for non-code rows: registry authentication denied on an image pull; a step exiting with "DEPLOY_TOKEN is not set"; a step fetching from an unreachable address with a short timeout to imitate a network flake.
- [ ] Delete the manual branch. Branches are always generated from patches so they can be recreated.

**A7. Scripts**
- [ ] `verify-patches.sh`: apply every patch to a clean checkout of `main`, fail if one does not apply.
- [ ] `create-branches.sh`: create `fail/NN-slug` from `main`, apply the patch, commit, push.
- [ ] `reset-branches.sh`: delete and recreate remote `fail/*` branches (use after `main` changes).
- [ ] A CI job in this repo that runs `verify-patches.sh` on every PR to `main`.
- [ ] Document usage in the testbed README.

### Part B. Main repo CI and test foundations
- [ ] `ci.yml`: pnpm install with cache, lint, typecheck, test, build, plus a Postgres service running `prisma migrate deploy` on an empty database.
- [ ] `packages/testing`: fake GitHub webhook payloads and a signature helper, a fake `GitHubClient`, test database setup and reset.
- [ ] Integration tests for the webhook endpoint with Yogesh, and for the failure worker with Dhruv.
- [ ] Coverage report in CI (no hard threshold yet).
- [ ] Each person still writes tests for their own features. Ishan provides the tools and the cross-module tests.

### Part C. Eval harness (`apps/eval`)
- [ ] CLI: `pnpm eval run --ids 01,02` (default: all).
- [ ] For each failure: re-run the workflow on its `fail/NN-slug` branch through the GitHub API, wait for the platform to process it, collect classification, outcome, and PR URL.
- [ ] Compare with `meta.json` and write a row per failure to `eval-results/YYYY-MM-DD.csv`.
- [ ] Print a summary: classification accuracy, outcome accuracy, validated-fix rate, secret leaks, median time.
- [ ] Keep result files in git to track progress.

### Part D. Fix validator (`packages/validator`, weeks 4-5)
- [ ] `validatePatch(repo, sha, patch)`: check out the commit in a temporary directory, apply the patch, run the same steps as the workflow (install, lint, typecheck, unit, integration, build).
- [ ] Run inside a container with CPU, memory, and time limits, and no access to secrets or the internal network.
- [ ] Return pass/fail per step and a short summary for the PR description.
- [ ] Tests with one known-good patch and one known-bad patch.

### Definition of done
`pnpm eval run` produces a scored table for all 20 failures, the testbed can be rebuilt from patches with one script, CI blocks broken PRs in the main repo, and `validatePatch` gives Dhruv a reliable pass/fail.

---

## 8. Common problems

- **Webhooks do not arrive:** check the tunnel URL in the GitHub App settings and the "Recent deliveries" tab (you can redeliver from there).
- **Signature check fails:** the raw request body must be used, not the parsed JSON.
- **Workflow does not run on a failure branch:** confirm the `fail/**` trigger and that Actions are enabled for the repo.
- **Old failure rows after rebuilding branches:** the commit ids changed. Clear them with `pnpm db:reset`.
- **Migration conflicts:** pull `main` before creating a migration. Never edit a merged one.
