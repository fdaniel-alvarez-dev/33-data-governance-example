#!/usr/bin/env python3
import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Finding:
    severity: str  # ERROR | WARN | INFO
    rule_id: str
    message: str
    path: str | None = None


def add(findings: list[Finding], severity: str, rule_id: str, message: str, path: Path | None = None) -> None:
    findings.append(
        Finding(
            severity=severity,
            rule_id=rule_id,
            message=message,
            path=str(path.relative_to(REPO_ROOT)) if path else None,
        )
    )


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def summarize(findings: list[Finding]) -> dict:
    return {
        "errors": sum(1 for f in findings if f.severity == "ERROR"),
        "warnings": sum(1 for f in findings if f.severity == "WARN"),
        "info": sum(1 for f in findings if f.severity == "INFO"),
    }


def check_no_company_branding(findings: list[Finding]) -> None:
    readme = REPO_ROOT / "README.md"
    if not readme.exists():
        return
    text = read_text(readme)
    if re.search(r"(?i)dexcom", text):
        add(findings, "ERROR", "docs.branding", "README contains company branding; keep it generic.", readme)


def check_ci_and_security(findings: list[Finding]) -> None:
    wf_dir = REPO_ROOT / ".github" / "workflows"
    if not wf_dir.exists():
        add(findings, "ERROR", "ci.missing", ".github/workflows is missing.", wf_dir)
        return

    workflows = sorted(wf_dir.glob("*.yml")) + sorted(wf_dir.glob("*.yaml"))
    if not workflows:
        add(findings, "ERROR", "ci.empty", "No GitHub Actions workflows found.", wf_dir)
        return

    has_gitleaks = any("gitleaks" in read_text(p) for p in workflows)
    if not has_gitleaks:
        add(findings, "WARN", "ci.gitleaks", "Consider enabling secret scanning (gitleaks) in CI.", wf_dir)

    has_demo_tests = any("TEST_MODE" in read_text(p) and "demo" in read_text(p) for p in workflows)
    if not has_demo_tests:
        add(findings, "WARN", "ci.demo_tests", "CI should run demo-mode tests offline and deterministically.", wf_dir)


def check_infra_examples(findings: list[Finding]) -> None:
    example = REPO_ROOT / "infra" / "examples" / "dev" / "main.tf"
    if not example.exists():
        add(findings, "WARN", "iac.example_missing", "Expected Terraform example missing at infra/examples/dev/main.tf.", example)
        return
    text = read_text(example)
    if "required_version" not in text:
        add(findings, "WARN", "iac.required_version", "Terraform example should include required_version.", example)
    if "required_providers" not in text:
        add(findings, "WARN", "iac.required_providers", "Terraform example should include required_providers.", example)


def check_gitignore(findings: list[Finding]) -> None:
    ignore = REPO_ROOT / ".gitignore"
    if not ignore.exists():
        add(findings, "ERROR", "gitignore.missing", ".gitignore is missing.", ignore)
        return
    text = read_text(ignore)
    for required in ["artifacts/", "data/processed/", ".[0-9][0-9]_*.txt", "*.pyc"]:
        if required not in text:
            add(findings, "WARN", "gitignore.rule", f"Consider adding gitignore rule: {required}", ignore)


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline multi-cloud DevOps guardrails for this repo.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--out", default="", help="Write output to a file (optional).")
    args = parser.parse_args()

    findings: list[Finding] = []
    check_no_company_branding(findings)
    check_ci_and_security(findings)
    check_infra_examples(findings)
    check_gitignore(findings)

    report = {"summary": summarize(findings), "findings": [asdict(f) for f in findings]}
    if args.format == "json":
        output = json.dumps(report, indent=2, sort_keys=True)
    else:
        lines = []
        for f in findings:
            where = f" ({f.path})" if f.path else ""
            lines.append(f"{f.severity} {f.rule_id}{where}: {f.message}")
        lines.append("")
        lines.append(f"Summary: {report['summary']}")
        output = "\n".join(lines)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)

    return 1 if report["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

