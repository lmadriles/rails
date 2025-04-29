SELECT FO.*,
    F.SiglaFerrovia,
    F.RazaoSocial,
    F.NomeMercadoria,
    F.DistanciaItinerario,
    F.Origem,
    F.Destino,
    F.concatenated_siglas
FROM fluxos_ocorrencias FO
LEFT JOIN fluxos F
ON FO.CodigoFluxoTransporteFerrovia || FO.SiglaFerrovia = F.id
