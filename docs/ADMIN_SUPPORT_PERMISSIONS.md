# Admin and Support Permissions

## Purpose

Document how the current UI reflects backend RBAC for inventory and collaborator operations.

## Backend RBAC Baseline

The backend already enforces permissions by route. The frontend should mirror those limits so operators understand what they can do before clicking.

## Role Matrix

| Role | Assets | Users | Imports | Macros | Audit Logs | Settings |
| --- | --- | --- | --- | --- | --- | --- |
| ADMIN | view, create, edit, move, delete | view, create, edit, delete | allowed | allowed | allowed | allowed |
| TECHNICIAN | view, create, edit, move | view, create, edit | allowed | allowed | denied | denied |
| MANAGER | view | view | denied | denied | allowed | denied |
| VIEWER | view | view | denied | denied | denied | denied |

## Frontend Signaling

- The shell now shows the access mode in the topbar.
- `/assets` shows a permission banner for read-only users and for operational users.
- `/users` still shows a clear consultation notice for non-write roles.
- Table empty states now provide contextual actions instead of a dead-end message.

## Support Guidance

- When a user reports “I cannot edit”, first check the role chip in the topbar.
- If the user is `VIEWER` or `MANAGER`, the missing actions are expected in inventory and collaborator pages.
- If an `ADMIN` or `TECHNICIAN` cannot see an action, that should be investigated as a UI or session issue.
