# Pdf Acrobat Workflow

## Required inputs
- purpose
- pdf_origin
- sensitivity
- has_signature
- has_certificate
- contains_personal_data
- needs_ocr
- needs_redaction
- is_final_or_editable
- human_validation_required

## Guardrails
- do not open real sensitive PDFs
- do not alter signed PDFs without approval
- do not call Adobe APIs in this phase
