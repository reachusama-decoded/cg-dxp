"""Relax Python's strict X509 flag for corp CA compatibility.

The corp CA bundle includes certificates that some Python/OpenSSL strict
validation paths reject when VERIFY_X509_STRICT is enabled. We only clear this
single strictness bit; hostname/expiry/chain validation remain intact.
"""

import ssl as _ssl

_orig_create_default_context = _ssl.create_default_context


def _create_default_context_relaxed(*args, **kwargs):
    ctx = _orig_create_default_context(*args, **kwargs)
    ctx.verify_flags &= ~_ssl.VERIFY_X509_STRICT
    return ctx


_ssl.create_default_context = _create_default_context_relaxed
_ssl._create_default_https_context = _create_default_context_relaxed

# urllib3/requests may create TLS contexts through urllib3's helper instead of
# ssl.create_default_context(), so patch that path as well when available.
try:
    from urllib3.util import ssl_ as _urllib3_ssl
except Exception:
    _urllib3_ssl = None

if _urllib3_ssl is not None:
    _orig_create_urllib3_context = _urllib3_ssl.create_urllib3_context

    def _create_urllib3_context_relaxed(*args, **kwargs):
        ctx = _orig_create_urllib3_context(*args, **kwargs)
        ctx.verify_flags &= ~_ssl.VERIFY_X509_STRICT
        return ctx

    _urllib3_ssl.create_urllib3_context = _create_urllib3_context_relaxed

# Some urllib3/requests paths mutate verify_flags after context creation.
# Clear STRICT immediately before handshake as a final guardrail.
_orig_wrap_socket = _ssl.SSLContext.wrap_socket


def _wrap_socket_relaxed(self, *args, **kwargs):
    self.verify_flags &= ~_ssl.VERIFY_X509_STRICT
    return _orig_wrap_socket(self, *args, **kwargs)


_ssl.SSLContext.wrap_socket = _wrap_socket_relaxed
