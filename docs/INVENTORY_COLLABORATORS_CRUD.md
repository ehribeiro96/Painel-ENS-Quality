# Inventory and Collaborators CRUD

## Inventory (`/assets`)

### Supported Operations

- List assets with filters and pagination.
- Create a new asset.
- Edit asset metadata.
- Move an asset.
- Send an asset back to stock.
- Deactivate an asset with history preserved.
- Open asset detail and history.

### UX Improvements in This Round

- Operational summary cards above the table.
- Permission banner that explains whether the current user can write.
- Richer empty state with an action button.
- Shared access-mode chip in the shell.

### Behavior Preserved

- Existing search and filter flow.
- Server-side pagination.
- Row-level actions.
- Delete remains soft/deactivation oriented.

## Collaborators (`/users`)

### Supported Operations

- List collaborators.
- Search by text.
- Create collaborator.
- Edit collaborator.
- Desactivate collaborator with history preserved.

### UX Improvements in This Round

- Summary cards for active users, admins and page coverage.
- Clearer read-only message.
- Empty state now offers a CTA to clear the search or create a collaborator.

### Behavior Preserved

- Backend source remains canonical for collaborator records.
- Manual creation stays separate from authentication and role edits.
- Soft delete still preserves historical references.
