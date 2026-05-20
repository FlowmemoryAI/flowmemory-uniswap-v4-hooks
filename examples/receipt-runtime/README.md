# Receipt Runtime Demo

Run:

```bash
python tools/receipt_runtime_demo.py --pretty
```

This demo shows the product loop around the hook:

```text
PolicyCard -> PulsePermit -> ActionPulse -> FlowPulseLink -> OutcomePulse -> PulsePass
```

It proves locally that a memory head can gate an action before execution and
that receipt evidence can settle the outcome afterward.

