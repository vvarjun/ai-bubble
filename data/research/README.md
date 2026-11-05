# Relationship evidence inventory

`relationships.csv` is a manually curated starting point, checked 5 November 2026. It is not comprehensive, automatically updated, a transaction ledger, or a cap table. An absent relationship does not mean that no relationship exists. Records preserve original disclosures, which can be amended, fulfilled, cancelled or superseded; verify current terms before analysis.

- `from_entity`, `to_entity`: investor → investee for investment records; buyer → provider for purchase commitments. These directions reflect the relationship, not verified cash flows.
- `relationship_type` and `status`: distinguish completed/partially completed investments from historical commitments. `partially_completed` means the source reports a portion participated in the financing, not how much of the original maximum remains outstanding.
- `disclosure_date`: date of the cited announcement or filing, not necessarily transaction or effective date.
- `amount_usd` and `amount_qualifier`: reported amount, not an estimate. `up_to` is a maximum, not money paid. Empty amounts mean unknown; ownership percentages are blank when not established.
- `source_url` and `notes`: primary source and context. R001/R003 and R002/R004 overlap; never sum them. R005 is the original 2025 Azure commitment, not necessarily its latest terms. R006 is one Amazon investment described in the S-1, not Amazon's full holdings.

The Microsoft–Anthropic two-node path combines investment and a purchase commitment. It is not a cycle of reciprocal stock ownership and does not establish that investment proceeds funded the purchase. The record dates are not simultaneous observations; do not infer that any historical relationship remains active today without verification. This dataset alone cannot quantify leverage, loss propagation or systemic risk.

## Source review, 5 November 2026

Anthropic's [2 November amended S-1](https://www.sec.gov/Archives/edgar/data/2130357/000162828026068676/anthropicpbc-sx1ax1.htm) updates the Microsoft arrangement and describes an AMD hardware framework and conditional stock purchase commitment. R007 replaces R005 as the later disclosure; they are not additive. AMD's investment is conditional and has not been recorded as completed ownership. AMD-based hardware may be sourced via third parties.

The [April 2026 Amazon announcement](https://www.anthropic.com/news/anthropic-amazon-compute) describes an AWS spending commitment alongside an investment. The [October S-1](https://www.sec.gov/Archives/edgar/data/2130357/000162828026067168/anthropicpbc-sx1.htm) describes separate Amazon and Google Series G-2 purchases; these rows are not comprehensive holdings. Anthropic's [Google–Broadcom announcement](https://www.anthropic.com/news/google-broadcom-partnership-compute) does not disclose separate amounts or contractual allocations for the two counterparties; R010 and R011 are two representations of one joint announcement.

These are manually selected primary-source records, not an exhaustive review of every company in the price basket, SEC holdings filing, or change after each disclosure. Ownership percentages remain unknown. Commitments span different years and conditions, and cannot be treated as realized revenue or directly added to investment amounts. FRED VIX is a market indicator, not relationship evidence; the Yahoo price download is separate from this inventory. No automatic SEC Company Facts or 13F ingestion has been implemented.
