WITH int_summary AS (
    SELECT * FROM {{ ref('int_prescriber_summary') }}
),

final AS (
    SELECT
        prescriber_npi,
        last_name,
        first_name,
        state,
        specialty,
        total_claims,
        total_drug_cost,
        total_beneficiaries,
        total_day_supply,
        total_30day_fills,
        unique_drugs_prescribed,
        avg_cost_per_claim,

        -- Derived risk indicators
        ROUND(total_drug_cost / NULLIF(total_beneficiaries, 0), 2)
            AS cost_per_beneficiary,
        ROUND(total_claims / NULLIF(unique_drugs_prescribed, 0), 2)
            AS claims_per_drug

    FROM int_summary
    WHERE total_claims > 0
      AND total_drug_cost > 0
)

SELECT * FROM final