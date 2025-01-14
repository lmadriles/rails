WITH fluxos_max_data AS (
    SELECT
        id,
        MAX(data) AS max_data
    FROM
        ocorrencias
    GROUP BY
        id
)
SELECT
    fluxos_intermed.*,
    fluxos_max_data.max_data
FROM
    fluxos_intermed
LEFT JOIN
    fluxos_max_data ON fluxos_intermed.id = fluxos_max_data.id
WHERE
    fluxos_max_data.max_data >= '{date}';
