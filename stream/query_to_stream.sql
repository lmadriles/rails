SELECT fluxos.*,
        intermed.intermed

FROM fluxos
LEFT JOIN intermed ON fluxos.id = intermed.id
