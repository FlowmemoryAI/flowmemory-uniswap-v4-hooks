# SLOs

These are target service levels for a future operated Base Sepolia reader.

They are not a production verifier network claim.

| SLO | Target | Measurement |
| --- | --- | --- |
| Reader lag | under 20 blocks for canary operation | `latestFinalizedBlock - cursorBlock` |
| Replay | replay from release start block within 15 minutes for canary ranges | PulseWatch replay output |
| Evidence freshness | public status regenerated within 10 minutes of release packet update | status page timestamp / packet hash |
| Cursor durability | no cursor rollback without explicit operator action | durable state diff |
| Error visibility | last error visible in health output | `pulse_watch.py health` |

If an SLO is missed, public status should degrade instead of upgrading evidence.
