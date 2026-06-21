# RELEASE-H1 - Final UAT Checklist

## Auth

```text
POST /api/v1/auth/login -> 200
access token present
token printed: NO
password printed: NO
```

Status: PASS for API smoke.

## Dashboard

```text
GET /api/v1/dashboard/summary -> 200
GET /api/v1/dashboard/assets-by-status -> 200
```

Status: PASS for API smoke.

## Users API

```text
GET /api/v1/users?page_size=100 -> 200
items=7
total=7
```

Status: PASS.

## Assets

```text
GET /api/v1/assets?page_size=20 -> 200
items=2
total=2
```

Status: PASS.

## Movement

Movement API was not mutated in this release checklist. Existing committed coverage and prior UAT evidence remain the reference.

Status: NOT MUTATED IN RELEASE-H1.

## Macro copy flow

The macro copy flow fix remains covered by prior MACRO-H1/H1B/H1C documentation. No new macro mutation was executed in this release checklist.

Status: DOCUMENTED PRIOR PASS, UI recheck remains separate if required.

## Asset history

```text
GET /api/v1/assets/{id}/history -> 200
items=1
```

Status: PASS.

## Audit logs

```text
GET /api/v1/audit-logs?page_size=20 -> 200
items=20
total=62
```

Filters:

```text
action -> 200
entity_type -> 200
entity_id -> 200
source -> 200
correlation_id -> 200
request_id -> 200
```

Status: PASS.

## AI Chat health

AI Chat was not exercised in this final release checklist. Existing security and provider documentation remain the reference.

Status: NOT RERUN IN RELEASE-H1.

## Settings

Settings page/UI was not browser-smoked in this boundary because authenticated UI smoke remains pending.

Status: PENDING UI-UAT-H1.

## UI smoke

Authenticated UI smoke is pending.

Known blocker:

```text
Browser in-app failed due permission resolving client under /mnt/c
```

Status: PARTIAL_UI_SMOKE_PENDING.

## Result

```text
GO_RELEASE_CANDIDATE_API_VALIDATED
PARTIAL_UI_SMOKE_PENDING
PARTIAL_DOCKER_PORT_PUBLISHING_BROKEN
```

The API UAT path is validated. Final UI sign-off remains required before a full production GO.
