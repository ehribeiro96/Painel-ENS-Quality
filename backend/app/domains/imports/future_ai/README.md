# Future AI Extension Point

This folder intentionally contains no AI implementation.

The import pipeline now isolates normalization, conflict detection and merge policy so future semantic deduplication can be added behind explicit interfaces without touching upload, staging or transactional merge code.

Planned future adapters:
- embedding-based probable duplicate detection
- semantic manufacturer/model normalization
- anomaly classification for suspicious inventory rows
