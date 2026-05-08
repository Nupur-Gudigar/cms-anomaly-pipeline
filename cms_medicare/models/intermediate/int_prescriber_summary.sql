WITH staging AS (
    SELECT * FROM {{ ref('stg_partd_prescribers') }}
),

aggregated AS (
    SELECT
        prescriber_npi,
        MAX(last_name)                  AS last_name,
        MAX(first_name)                 AS first_name,
        MAX(state)                      AS state,
        MAX(specialty)                  AS specialty,

        -- Aggregate billing metrics across all drugs
        SUM(total_claims)               AS total_claims,
        SUM(total_drug_cost)            AS total_drug_cost,
        SUM(total_beneficiaries)        AS total_beneficiaries,
        SUM(total_day_supply)           AS total_day_supply,
        SUM(total_30day_fills)          AS total_30day_fills,

        -- Count unique drugs prescribed
        COUNT(DISTINCT brand_name)      AS unique_drugs_prescribed,

        -- Average cost per claim
        CASE
            WHEN SUM(total_claims) > 0
            THEN SUM(total_drug_cost) / SUM(total_claims)
            ELSE 0
        END                             AS avg_cost_per_claim

    FROM staging
    GROUP BY prescriber_npi
)

SELECT * FROM aggregated