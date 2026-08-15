"""
hivimpact — a contamination-safe pipeline for tracking the impact of global-health
funding cuts (PEPFAR / USAID / UNAIDS) on HIV services across LMICs.

Design principles (see DESIGN.md):
  1. Reliability & validity first. Structured/authoritative feeds only; never parse
     prose/PDFs for numbers. An honest "not published" beats a fabricated figure.
  2. No mass-LLM extraction anywhere in the pipeline.
  3. Provenance on every row (source_url + retrieved_at + source_type).
  4. Triangulation, not blind trust: country/source data is primary; aggregators are
     a cross-check. Discrepancies are findings, not just errors.

Phase 1 (this package) builds the aggregator layer: UNAIDS AIDSinfo, WHO GHO,
OECD CRS/DAC, and the World Bank (denominators). These are few, structured and
near-global, and form the reliable baseline + triangulation reference.
"""

__version__ = "0.1.0"
