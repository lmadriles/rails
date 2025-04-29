SELECT
    A.CodigoAcidente,
    A.CodigoNaturezaAcidente,
    A.CodigoCausaAcidente,
    A.CodigoFerroviaOutra,
    A.CodigoFerroviaResponsavel,
    A.CodigoLinha,
    A.DataHoraOcorrencia,
    A.IndicadorAcidenteGrave,
    A.IndicadorConfirmado,
    CAST(A.NumeroQuilometroInicial AS REAL) AS NumeroQuilometroInicial,
    CAST(A.NumeroQuilometroFinal AS REAL) AS NumeroQuilometroFinal,
    CAST(A.LongitudeInicialAcidente AS REAL) AS LongitudeInicialAcidente,
    CAST(A.LatitudeInicialAcidente AS REAL) AS LatitudeInicialAcidente,
    CAST(A.LongitudeFinalAcidente AS REAL) AS LongitudeFinalAcidente,
    CAST(A.LatitudeFinalAcidente AS REAL) AS LatitudeFinalAcidente,
    A.IndicadorAcidenteExcluido,
    A.CodigoCausaAcidenteDireta,
	EA.CodigoTresLetrasEstacao AS EstacaoAnterior,
    EP.CodigoTresLetrasEstacao AS EstacaoPosterior,
    CAST(A.the_geomInicialAcidente AS VARCHAR(MAX)) AS geometry_inicial,
    CAST(A.the_geomFinalAcidente AS VARCHAR(MAX)) AS geometry_final

FROM [BD_SAFF].[dbo].[tblAcidente] A
INNER JOIN [BD_SAFF].[dbo].[tblFerrovia] F
    ON A.CodigoFerrovia = F.CodigoFerrovia
INNER JOIN [BD_SAFF].[dbo].[tblEstacao] EA
    ON A.CodigoEstacaoAnterior = EA.CodigoEstacao
INNER JOIN [BD_SAFF].[dbo].[tblEstacao] EP
    ON A.CodigoEstacaoPosterior = EP.CodigoEstacao

WHERE A.DataHoraOcorrencia BETWEEN '2019-01-01' AND '2024-12-31';