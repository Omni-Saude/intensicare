# RULE-DOCUMENTACAO-FATURAMENTO-030 — PDF grouping response status-code decision tree

| Field | Value |
|---|---|
| Category | data-validation |
| Type | decision-tree |
| Status | OK |
| Verification | NOT_APPLICABLE |
| Confidence | high |
| Cluster | documentacao-faturamento |

## Rule
retrieve_multiple maps distinct failure modes from the external retrieve-multiple call and downstream PDF-combining step to specific HTTP status codes: external 401 -> 401 with an auth-failure message; any requests exception -> 500; unexpected response shape (neither list nor dict) -> 500; empty resulting URL list -> 400; combinar_documentos returning an 'errors' key -> whatever status it specifies (default 400); success -> 200 with the combined file path.

## Inputs
| Name | Type | Unit | Range |
|---|---|---|---|
| external response status/body | object |  |  |

## Outputs
| Name | Type | Unit |
|---|---|---|
| http_status | integer |  |

## Logic
```text
response = session.post(retrieve_multiple_url, json={"ids": ids}, headers={"X-Api-Key": AMHDOCS_APIKEY}, timeout=10)
if response.status_code == 401: return Response({...}, status=401)
response.raise_for_status()   # raises on other non-2xx, caught below -> 500
data = response.json()
if isinstance(data, list):
    id_to_url = {item["id"]: item["url_bucket"] for item in data if "id" in item and "url_bucket" in item}
    urls = [id_to_url[i] for i in ids if i in id_to_url]
elif isinstance(data, dict):
    urls = data.get("pdf_urls", [])
else:
    return Response({...}, status=500)
if not urls:
    return Response({...}, status=400)
caminho_arquivo = combinar_documentos(urls, bucket_name, s3_directory)
if "errors" in caminho_arquivo:
    return Response(caminho_arquivo, status=caminho_arquivo.get("status", 400))
return Response({"message": "...", "file_path": caminho_arquivo["url"]}, status=200)
```

## Edge cases (as implemented)
requests.exceptions.RequestException (network errors, raise_for_status() 4xx/5xx other than 401) is caught and mapped to 500 regardless of the actual external status code.

## Verification
Not applicable — non-formula rule; behavior is defined by the cited legacy source.

## Provenance
| Repo | Path | Lines | Commit | Role |
|---|---|---|---|---|
| ahlabs-trilhas | core/api/v1/views/integracao_amhdocs.py | 68-130 | 8166c07e | primary |
- Merged from: RULE-integracao-BE-05-004
- Related rules: RULE-DOCUMENTACAO-FATURAMENTO-029, RULE-DOCUMENTACAO-FATURAMENTO-003, RULE-DOCUMENTACAO-FATURAMENTO-016

## Notes
combinar_documentos implementation lives in utils.combinar_documentos, out of this partition's scope.

*Extracted from ahlabs-trilhas@8166c07e and trilhas-frontend@f9656be2 — IntensiCare legacy rule audit, 2026-07-03. Do not edit by hand; the reconciled catalog is the source of truth.*
