SELECT 
    F.*, 
    MIN(FO.DataReferencia) AS data_minima,
    MAX(FO.DataReferencia) AS data_maxima
    
FROM fluxos F
LEFT JOIN fluxos_ocorrencias FO
ON F.id = FO.id
WHERE 
    F.DistanciaItinerario > 0 
    AND F.DistanciaItinerario IS NOT NULL
GROUP BY F.id;
