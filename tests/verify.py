#!/usr/bin/env python3
"""Exercise the actual bbs generator, frozen install, checks and live API."""
import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import tempfile
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from harness import check_project

ROOT = Path(__file__).resolve().parents[1]
BBS = os.environ.get("BBS_BIN", "bbs")


def bbs(*args, success=True):
    result = subprocess.run([BBS, *map(str, args)], text=True, capture_output=True)
    if (result.returncode == 0) != success:
        raise AssertionError(f"bbs {args}: exit {result.returncode}\n{result.stdout}\n{result.stderr}")
    if success:
        print(result.stderr, end="", flush=True)
    return result


def files(project):
    result = {}
    for parent, dirs, names in os.walk(project):
        dirs[:] = [d for d in dirs if d not in {"node_modules", "dist", ".git", ".next"}]
        for name in names:
            path = Path(parent) / name
            body = path.read_bytes()
            assert b"__PROJECT_NAME__" not in body and b"__GIT_PROFILE__" not in body, path
            result[str(path.relative_to(project))] = hashlib.sha256(body).hexdigest()
    return result


def request(port, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = Request(f"http://127.0.0.1:{port}{path}", data=data, headers={"Content-Type": "application/json"})
    try:
        response = urlopen(req, timeout=1)
    except HTTPError as error:
        response = error
    with response:
        return response.code, json.load(response), response.headers.get("x-request-id")


def page(port, path):
    try:
        response = urlopen(f"http://127.0.0.1:{port}{path}", timeout=5)
    except HTTPError as error:
        response = error
    with response:
        return response.code, response.read().decode()


def serve(project, command, ready_path, probe, env=None):
    """Start the built project on a free port, wait for ready_path, run probe(port)."""
    with socket.socket() as reservation:
        reservation.bind(("127.0.0.1", 0))
        port = reservation.getsockname()[1]
    env = {**os.environ, **(env or {}), "PORT": str(port)}
    with tempfile.TemporaryFile(mode="w+") as log:
        process = subprocess.Popen(command, cwd=project, env=env,
                                   stdout=log, stderr=log, start_new_session=True)
        try:
            deadline = time.monotonic() + 30
            while True:
                if process.poll() is not None:
                    log.seek(0)
                    raise AssertionError(f"server exited before readiness: {log.read()}")
                try:
                    if page(port, ready_path)[0] == 200:
                        break
                except OSError:
                    pass
                if time.monotonic() > deadline:
                    raise AssertionError(f"local generated project did not become ready: {project.name}")
                time.sleep(0.2)
            probe(port)
        finally:
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
            process.wait(timeout=10)


def live_next(project):
    def probe(port):
        status, body = page(port, "/")
        assert status == 200 and project.name in body, "home page did not render the project"
        status, body = page(port, "/missing")
        assert status == 404 and "Page not found" in body, "unknown route did not render the 404 page"
        print("PASS local generated web: home page, 404 page", flush=True)
    serve(project, ["pnpm", "start"], "/", probe)


def live_hono(project):
    def probe(port):
        assert request(port, "/readyz")[0] == 200
        status, body, request_id = request(port, "/greetings", {"name": "Long", "locale": "vi"})
        assert status == 200 and body == {"message": "Xin chào, Long!"} and request_id
        for input_body in [{"name": ""}, {"name": "Long", "locale": "fr"}]:
            status, body, request_id = request(port, "/greetings", input_body)
            assert status == 400 and body["error"]["requestId"] == request_id
        status, body, request_id = request(port, "/missing")
        assert status == 404 and body["error"]["requestId"] == request_id
        print("PASS local generated API: health/readiness, greeting, invalid inputs, 404", flush=True)
    serve(project, ["bun", "run", "start"], "/healthz", probe, {"NODE_ENV": "test"})


def main():
    catalog = json.loads((ROOT / "catalog.json").read_text())
    with tempfile.TemporaryDirectory(prefix="2build-starters-test-") as temporary:
        work = Path(temporary)
        for template_id in catalog["templates"]:
            project = work / f"sample-{template_id}"
            result = bbs("bootstrap", project, "--template", template_id,
                         "--source", ROOT, "--version", catalog["version"], "--json")
            handoff = json.loads(result.stdout)
            assert handoff["verified"] is True
            assert handoff["starter"]["release"] == catalog["version"]
            assert handoff["starter"]["revision"].startswith("sha256:")
            assert json.loads((project / "package.json").read_text())["name"] == project.name
            assert not (project / ".babysit/git-flow.yaml").exists()
            assert not (project / ".env").exists()
            findings = check_project(project, catalog["templates"][template_id])
            assert not findings, f"generated project fails the harness-audit contract: {findings}"
            before = files(project)
            bbs("bootstrap", project, "--source", ROOT, success=False)
            assert files(project) == before, "overwrite refusal changed existing files"
            rejected = work / f"rejected-{template_id}"
            bbs("bootstrap", rejected, "--source", ROOT, "--template", "missing", success=False)
            assert not rejected.exists()

            # A release check must retain project-specific edits and provenance.
            (project / "README.md").write_text((project / "README.md").read_text() + "\nProduct-specific note.\n")
            before = files(project)
            newer = work / f"newer-{template_id}"
            newer.mkdir()
            next_catalog = json.loads(json.dumps(catalog))
            major, minor, patch = map(int, catalog["version"].split("."))
            next_catalog["version"] = f"{major}.{minor}.{patch + 1}"
            next_catalog["templates"][template_id]["revision"] += 1
            (newer / "catalog.json").write_text(json.dumps(next_catalog))
            checked = json.loads(bbs("starter", "check", "--dir", project / "src", "--source", newer, "--json").stdout)
            assert checked["status"] == "update_available" and checked["upgrade_url"]
            assert files(project) == before, "release check modified product code or lock"
            if template_id == "hono-bun":
                live_hono(project)
            elif template_id == "nextjs-pnpm":
                live_next(project)
            print(f"PASS {template_id}: generation, checks, provenance, refusal and advisory update", flush=True)


if __name__ == "__main__":
    main()
