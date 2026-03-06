# 33-aws-reliability-security-oracle

A portfolio-grade repository that demonstrates **multi-cloud DevOps validation patterns**:
offline-safe demos, deterministic guardrails, and explicit “demo vs production” test modes.


## The top pains this repo addresses
1) Designing a resilient, scalable cloud platform foundation—Kubernetes/container orchestration, networking, and standard patterns teams can reuse.
2) Replacing manual, risky changes with automated delivery—repeatable infrastructure, safe deployments, and drift-free environments (IaC + CI/CD + GitOps).
3) Building a data platform people trust—reliable pipelines, clear ownership, data quality checks, and governance that scales without slowing delivery.

## Quick demo (local)
```bash
make demo-offline
make test
```

What you get:
- an offline demo pipeline output (no pip installs needed)
- a multicloud guardrails report (`artifacts/multicloud_guardrails.json`)
- explicit `TEST_MODE=demo|production` tests with safe production gating

## Tests (two explicit modes)

- `TEST_MODE=demo` (default): offline-only checks, deterministic artifacts
- `TEST_MODE=production`: real integrations (requires explicit opt-in + dependencies)

Run demo mode:

```bash
make test-demo
```

Run production mode:

```bash
make test-production
```

Optional production checks:
- Set `TERRAFORM_VALIDATE=1` to validate `infra/examples/dev/` (requires `terraform`)

## Guardrails

Generate evidence:

```bash
python3 tools/multicloud_guardrails.py --format json --out artifacts/multicloud_guardrails.json
```

## Sponsorship and contact

Sponsored by:
CloudForgeLabs  
https://cloudforgelabs.ainextstudios.com/  
support@ainextstudios.com

Built by:
Freddy D. Alvarez  
https://www.linkedin.com/in/freddy-daniel-alvarez/

For job opportunities, contact:
it.freddy.alvarez@gmail.com

## License

Personal, educational, and non-commercial use is free. Commercial use requires paid permission.
See `LICENSE` and `COMMERCIAL_LICENSE.md`.
