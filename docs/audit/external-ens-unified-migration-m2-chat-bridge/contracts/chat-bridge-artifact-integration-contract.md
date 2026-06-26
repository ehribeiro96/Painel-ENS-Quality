# Chat Bridge Artifact Integration Contract

This document defines how the Hermes Chat Bridge adapter interacts with the Artifact Server contract from M1.

## Key rule

M1 is still `M1A_CONTRACT_ONLY`, so any flow that needs durable upload, download, delete or signed access-link minting is currently BLOCKED_UNTIL_ARTIFACT_IMPLEMENTATION.

## Required behaviors

- User attachments are accepted only through backend DTOs.
- The frontend never receives raw storage paths or direct bucket credentials.
- The adapter may normalize attachment text, image inputs and file metadata.
- When artifact support is unavailable, attachment-bearing runs should degrade to documented fallback behavior instead of attempting a direct client-side upload.
- `artifact.created` and `artifact.updated` are reserved events for the future durable artifact flow.

## Attachment policy

- enforce MIME allowlists
- enforce request size limits
- enforce maximum attachment count
- enforce owner/session prefix checks
- reject suspicious paths
- keep signed URLs short-lived

## Artifact mapping

The external bridge already imports files into artifact storage and rewrites assistant URLs after import.
That behavior is valid as a conceptual contract, but it should not be enabled in the current runtime until the M1 contract gains a real backend implementation.

## Rejected shortcut

The adapter must not copy the legacy service wholesale, and it must not let the frontend talk directly to provider or storage endpoints.
