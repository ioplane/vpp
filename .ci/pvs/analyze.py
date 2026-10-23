# /// script
# requires-python = ">=3.14"
# dependencies = []
# ///
"""PVS tool-health gate and unsuppressed NAT/IKE reports for the trusted fork."""

import base64
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

FILES = {
    "src/plugins/nat/nat44-ed/nat44_ed.c",
    "src/plugins/nat/nat44-ed/nat44_ed_api.c",
    "src/plugins/nat/nat44-ed/nat44_ed_cli.c",
    "src/plugins/nat/nat44-ed/nat44_ed_in2out.c",
    "src/plugins/ikev2/ikev2.c",
}


def main():
    root = Path.cwd()
    output = root / "pvs-report"
    output.mkdir(exist_ok=True)
    encoded = os.environ.pop("PVS_LICENSE_B64")
    credential = base64.b64decode(encoded, validate=True).decode().splitlines()
    if len(credential) != 2 or not all(credential):
        raise ValueError("PVS_LICENSE_B64 must contain a two-line license file")

    def redact(value):
        for secret in [encoded, *credential]:
            value = value.replace(secret, "[redacted]")
        return value

    with tempfile.TemporaryDirectory(dir="/run/pvs") as temporary:
        work = Path(temporary)
        os.environ["TMPDIR"] = temporary
        license_path = work / "PVS-Studio.lic"
        with os.fdopen(
            os.open(license_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w"
        ) as stream:
            stream.write("\n".join(credential) + "\n")

        def execute(arguments):
            result = subprocess.run(
                arguments,
                check=False,
                cwd=work,
                text=True,
                capture_output=True,
                timeout=600,
            )
            return result.returncode, redact(result.stdout + result.stderr)

        def convert(log, kind, mask, target):
            code, text = execute(
                [
                    "plog-converter",
                    "-a",
                    mask,
                    "-t",
                    kind,
                    "-r",
                    str(root),
                    "-o",
                    str(target),
                    str(log),
                ]
            )
            if code:
                raise RuntimeError("PVS report conversion failed: " + text)
            target.write_text(redact(target.read_text()))

        def analyze(database, name):
            log = work / (name + ".log")
            code, text = execute(
                [
                    "pvs-studio-analyzer",
                    "analyze",
                    "-f",
                    str(database),
                    "-l",
                    str(license_path),
                    "-o",
                    str(log),
                    "-j",
                    "2",
                ]
            )
            (output / (name + "-process.log")).write_text(text)
            if code or re.search(
                r"can't be preprocessed|can't create", text, re.IGNORECASE
            ):
                raise RuntimeError(
                    "PVS analysis or preprocessing failed; inspect sanitized process log"
                )
            errors = work / (name + "-errors.json")
            convert(log, "json", "FAIL:1,2,3", errors)
            if json.loads(errors.read_text())["warnings"]:
                raise RuntimeError("PVS reported analysis failures")
            return log

        probe = work / "probe.c"
        probe.write_text("int main(void) { int *p = 0; return *p; }\n")
        database = work / "probe-commands.json"
        database.write_text(
            json.dumps(
                [
                    {
                        "directory": temporary,
                        "file": str(probe),
                        "command": f"/usr/bin/clang -c {probe} -o {work / 'probe.o'}",
                    }
                ]
            )
        )
        log = analyze(database, "control")
        control = work / "control.json"
        convert(log, "json", "GA:1,2,3", control)
        if not any(
            w["code"] == "V522" for w in json.loads(control.read_text())["warnings"]
        ):
            raise RuntimeError("PVS positive control did not detect V522")

        entries = json.loads((root / "build-pvs/compile_commands.json").read_text())
        expected = {str(root / name) for name in FILES}
        selected = [entry for entry in entries if entry["file"] in expected]
        if len(selected) != len(expected) or {e["file"] for e in selected} != expected:
            raise RuntimeError("Expected exactly five NAT/IKE compilation entries")
        database = work / "commands.json"
        database.write_text(json.dumps(selected))
        log = analyze(database, "vpp")
        for kind in ("json", "sarif", "gitlab", "totals"):
            convert(log, kind, "GA:1,2,3", output / ("vpp." + kind))
        codequality = output / "vpp.gitlab"
        issues = json.loads(codequality.read_text())
        for issue in issues:
            issue["location"]["path"] = (
                Path(issue["location"]["path"]).relative_to(root).as_posix()
            )
        codequality.write_text(json.dumps(issues) + "\n")
        warnings = json.loads((output / "vpp.json").read_text())["warnings"]
        source_sha = (root / ".pvs-source-sha").read_text().strip()
        if not re.fullmatch(r"[0-9a-f]{40}", source_sha):
            raise RuntimeError("Invalid source provenance")
        summary = {
            "source_sha": source_sha,
            "translation_units": len(selected),
            "positive_control": "V522",
            "warnings": len(warnings),
            "warning_policy": "report-only; no suppressions",
        }
        (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        print(json.dumps(summary), file=sys.stderr)


if __name__ == "__main__":
    try:
        main()
    finally:
        with tarfile.open(fileobj=sys.stdout.buffer, mode="w|gz") as archive:
            for name in (
                "control-process.log",
                "vpp-process.log",
                "summary.json",
                "vpp.json",
                "vpp.sarif",
                "vpp.gitlab",
                "vpp.totals",
            ):
                path = Path("pvs-report") / name
                if path.is_file():
                    archive.add(path, arcname=name)
