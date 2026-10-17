# What I Would Do With One More Week
**Candidate Perspective | Engineering Roadmap & Prioritized Enhancements**  
**Project Atlas — AI Research Copilot | Cognitive Market Research and Consulting**  

---

If granted one additional week to build upon this foundational architecture, I would prioritize high-impact enhancements across retrieval quality, multi-modal ingestion, analyst workflows, and production hardening:

---

## 1. Hybrid Search (Dense Vector + BM25) & Cross-Encoder Reranking
* **Why it matters:** Pure dense vector search can struggle with exact acronyms (e.g. *DLMS/COSEM*, *NB-IoT*, *AMI vs AMR*) or specific product codes.
* **Implementation Plan:**
  * Implement reciprocal rank fusion (RRF) combining ChromaDB dense cosine similarity with an in-memory BM25 index (e.g., `rank-bm25`).
  * Introduce a lightweight, local cross-encoder reranker (e.g., `flashrank` or `bge-reranker-base`) to score the top-20 retrieved chunks down to the top-5 most relevant passages before prompt assembly.
  * Benchmark precision and recall gains against our existing 25-case evaluation dataset.

---

## 2. Multi-Modal PDF & Chart Ingestion Pipeline
* **Why it matters:** Syndicated market research reports frequently communicate essential baseline shares, CAGR curves, and vendor matrices through embedded infographic charts and tables rather than prose.
* **Implementation Plan:**
  * Integrate an advanced document parser such as `Docling` or `PyMuPDF4LLM` to extract tabular data into structured markdown and JSON tables.
  * Add a visual grounding pipeline using vision-capable models (e.g., Gemini 1.5 Flash Vision) to transcribe and verify chart figures directly, attaching bounding-box coordinates to chunk provenance metadata.

---

## 3. Human-in-the-Loop Analyst Workbench & SLA Webhooks
* **Why it matters:** When questions are escalated (e.g., custom 2035 horizons, complex econometric extrapolations), human analysts currently view tickets via the `/escalations` view, but have no live editorial response flow.
* **Implementation Plan:**
  * Build a collaborative analyst workbench in CodeIgniter 3 enabling research directors to claim tickets, draft bespoke answers with verified data attachments, and resolve tickets.
  * Implement automated webhook notifications (SendGrid / Slack / Webhook dispatch) to notify corporate procurement heads when an analyst has completed their escalated review.

---

## 4. Production Auth & Entitlement Hardening (OAuth2 / JWT / SSO)
* **Why it matters:** The current take-home implementation models authenticated client identity via secure server sessions and API keys.
* **Implementation Plan:**
  * Upgrade the interface between CodeIgniter 3 and FastAPI to use cryptographically signed JSON Web Tokens (RS256 JWTs) carrying verified tenant claims (`client_id`, `purchased_report_ids`).
  * Add SAML 2.0 / Okta / Azure AD enterprise single sign-on (SSO) integration for corporate utility clients.

---

## 5. Entitlement-Aware Semantic Caching
* **Why it matters:** Repeated market questions across utility consortiums can drive redundant computation and latency.
* **Implementation Plan:**
  * Implement a Redis-backed semantic cache with composite cache keys:
    `cache_key = SHA256(client_entitlements_hash + normalized_question_embedding)`
  * Ensure that cache invalidation triggers automatically whenever a new report edition or corrigendum is ingested, strictly preventing cross-tenant leakage.

---

## 6. Distributed Observability & Guardrail Evals
* **Why it matters:** Enterprise deployments require real-time tracing of token spend, latency anomalies, and automated jailbreak detection.
* **Implementation Plan:**
  * Deploy self-hosted `Langfuse` or `OpenInference` instrumentation to log token cost, model latency, and prompt traces.
  * Integrate `NeMo Guardrails` or `Llama Guard` as an additional asynchronous safety layer running parallel to our regex/AST validation engine.
