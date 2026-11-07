"""Offline certificate wiring checks for local/devcontainer workflows."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
DBT_WRAPPER = REPO_ROOT / "dbt_wrapper.py"
MISE_ENV = REPO_ROOT / ".mise" / "env.sh"
DEVCONTAINER_DOCKERFILE = REPO_ROOT / ".devcontainer" / "Dockerfile"
SITECUSTOMIZE = REPO_ROOT / ".devcontainer" / "sitecustomize.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_devcontainer_ca_bundle_symlinks_present() -> None:
    """The devcontainer image should expose the CA bundle in common Linux locations."""
    dockerfile = _read(DEVCONTAINER_DOCKERFILE)
    assert "/cacert.pem" in dockerfile
    assert "/etc/ssl/certs/ca-certificates.crt" in dockerfile
    assert "/etc/pki/tls/certs/ca-bundle.crt" in dockerfile


def test_mise_env_exports_tls_env_vars() -> None:
    """The shell bootstrap should export TLS env vars used by Python/OpenSSL clients."""
    env_script = _read(MISE_ENV)
    assert "export REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt" in env_script
    assert "export SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt" in env_script


def test_dbt_wrapper_declares_cert_fallback_paths() -> None:
    """dbt wrapper should include CA fallback locations for heterogeneous runtimes."""
    wrapper = _read(DBT_WRAPPER)
    assert 'for _cert_var in ("REQUESTS_CA_BUNDLE", "SSL_CERT_FILE", "CURL_CA_BUNDLE")' in wrapper
    assert "/etc/ssl/certs/ca-certificates.crt" in wrapper
    assert "/etc/pki/tls/certs/ca-bundle.crt" in wrapper
    assert "/etc/ssl/ca-bundle.pem" in wrapper


def test_dbt_wrapper_prefers_repo_custom_cert_when_present() -> None:
    """If the repo CA cert exists, dbt wrapper should wire it for requests/OpenSSL."""
    wrapper = _read(DBT_WRAPPER)
    assert '"init_scripts", "certs", "cacert.pem"' in wrapper
    assert 'os.environ["REQUESTS_CA_BUNDLE"] = _custom_cert' in wrapper
    assert 'os.environ["SSL_CERT_FILE"] = _custom_cert' in wrapper


def test_dbt_wrapper_bootstraps_dbt_when_missing_on_shared_clusters() -> None:
    wrapper = _read(DBT_WRAPPER)
    assert "def _ensure_dbt_available(project_dir: str | None) -> None:" in wrapper
    assert 'pip", "install", "--quiet", "-r", requirements_path' in wrapper
    assert '"databricks-sql-connector"' in wrapper


def test_devcontainer_dockerfile_installs_dpc_scripts() -> None:
    dockerfile = _read(DEVCONTAINER_DOCKERFILE)
    # The image must install the dockerd helper scripts used by the repo.
    expected = ("start-dockerd.sh", "ensure-dockerd.sh", "post-start.sh", "check.sh")
    assert all(s in dockerfile for s in expected), "Dockerfile must install dockerd helper scripts: start/ensure/post-start/check"


def test_devcontainer_installs_ssl_sitecustomize() -> None:
    dockerfile = _read(DEVCONTAINER_DOCKERFILE)
    assert SITECUSTOMIZE.is_file()
    assert "COPY .devcontainer/sitecustomize.py" in dockerfile
    assert "VERIFY_X509_STRICT" in _read(SITECUSTOMIZE)
    assert "create_urllib3_context" in _read(SITECUSTOMIZE)
    assert "SSLContext.wrap_socket" in _read(SITECUSTOMIZE)
