# Round Table Shell

The Round Table shell is a static public preview for future multi-agent collaboration inside Sparkbot.

The current public shell baseline includes a read-only surface in the Workstation shell. It shows the intended seat model without enabling meeting behavior, chat, model calls, turn-taking, orchestration, tool execution, provider setup, or guarded runtime controls.

## Preview seats

- Operator: human direction for a future session.
- Assistant seat: planned general support participant.
- Research seat: planned information review participant.
- Builder seat: planned implementation planning participant.
- Reviewer seat: planned quality review participant.

## Current behavior

- The preview renders inside the Workstation shell.
- Seat cards are inert and read-only.
- Labels use preview or planned status.
- The existing backend health check remains the only frontend action.

## Excluded from this baseline

- Meeting creation or joining.
- Chat input or message sending.
- Model provider calls.
- Meeting manager logic.
- Turn-taking engine.
- Agent orchestration.
- Tool execution.
- Terminal or file mutation features.
- Provider setup forms.
- Guardian runtime controls.

## Next public slice

The next slice should document the public interaction contract before adding any active behavior. Implementation should stay local-first, guarded by clear validation, and honest about what is available in the current release.
