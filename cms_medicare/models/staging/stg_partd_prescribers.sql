WITH source AS (
    SELECT * FROM {{ source('raw', 'partd_prescribers') }}
),

renamed AS (
    SELECT
        -- Prescriber identity
        PRSCRBR_NPI                 AS prescriber_npi,
        PRSCRBR_LAST_ORG_NAME       AS last_name,
        PRSCRBR_FIRST_NAME          AS first_name,
        PRSCRBR_CITY                AS city,
        PRSCRBR_STATE_ABRVTN        AS state,
        PRSCRBR_TYPE                AS specialty,

        -- Drug information
        BRND_NAME                   AS brand_name,
        GNRC_NAME                   AS generic_name,

        -- Core billing metrics
        TOT_CLMS                    AS total_claims,
        TOT_30DAY_FILLS             AS total_30day_fills,
        TOT_DAY_SUPLY               AS total_day_supply,
        TOT_DRUG_CST                AS total_drug_cost,
        TOT_BENES                   AS total_beneficiaries,

        -- 65+ patient metrics
        GE65_TOT_CLMS               AS total_claims_ge65,
        GE65_TOT_DRUG_CST           AS total_drug_cost_ge65,
        GE65_TOT_BENES              AS total_beneficiaries_ge65

    FROM source
)

SELECT * FROM renamed