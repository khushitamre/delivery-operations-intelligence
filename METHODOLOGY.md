# Methodology and Interview Guide

## Business framing

The product investigates delivery promise variance and customer-experience risk in an e-commerce marketplace. It does not claim to be an internal analysis of a named delivery company. The public Olist data is used as a realistic benchmark for demonstrating how an operations analyst would structure the investigation.

## Analytical workflow

**Ingest.** Read the six source tables from `data/raw/` and preserve source-level identifiers.

**Standardise.** Parse lifecycle timestamps, map product categories to English labels, and aggregate order-item facts to one row per order.

**Join.** Join the order table to customer, seller, item and review dimensions. The order grain prevents item count from inflating order-level service rates.

**Define.** Measure `delivery_days`, `promised_days`, `late_days`, `is_late`, `is_cancelled` and review health using explicit denominators documented in `DATA_DICTIONARY.md`.

**Diagnose.** Segment service risk by time, market, category and seller. Apply volume thresholds to avoid overreacting to small samples.

**Prioritise.** Use the seller queue and the Decision Lab to turn analysis into an operational pilot hypothesis.

**Validate.** Run `python validate_data.py` after ETL. The app is smoke-tested by launching Streamlit and requesting its health endpoint.

## Interview narrative

> I started with the operational question rather than the chart. The first question was where service risk is concentrated, so I set the denominator to delivered orders and applied minimum-volume guardrails. I then linked late delivery to review health to quantify the customer consequence. Finally, I created an intervention queue and a scenario tool. Because the public data does not include rider telemetry, weather or preparation timestamps, I treat those as future instrumentation requirements instead of presenting unsupported root causes.

## Recommended next data collection

A production version should add event-level timestamps for order acceptance, seller dispatch, carrier pickup, first delivery attempt and final delivery; rider or carrier assignment; route distance; weather; traffic; and promised-versus-actual SLA at the order level. With those fields, operations could test causal hypotheses and monitor an agreed service-level objective.

## Ethical and governance controls

The data is anonymised. The dashboard does not expose customer names. Review text is not displayed. Risk scores are prioritisation aids, not accusations. Scenario outputs are labelled directional. Human operations owners remain responsible for validating any intervention.
