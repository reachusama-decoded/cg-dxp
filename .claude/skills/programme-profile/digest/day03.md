# Decision digest — S03 AI product design, FastAPI and hosted-model calls with AI frameworks (U2 M1–M3)

Working title; MJB confirms. Session order confirmed by MJB on 2026-10-13 (see general.md). Dated, confirmed decisions that constrain other modules go here. Newest last.

**2026-10-15 — LangChain is the client stack (user).** M3 shows one raw API call to demystify the vendor, then makes the same call through LangChain's chat model pointed at the Decoded proxy, with a Pydantic model enforced on the result. See general.md.
