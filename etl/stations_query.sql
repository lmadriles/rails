SELECT
    LE.CodigoLinhaEstacao,
    F.SiglaFerrovia,
    L.NomeLinha,
    E.CodigoTresLetrasEstacao,
    E.NomeEstacao,
	M.NomeMunicipio,
	UF.SiglaUF,
    LE.NumeroSequencia,
    CAST(LE.NumeroExtensao AS REAL) AS NumeroExtensao,
    E.IndicadorPorto,
    E.IndicadorTerminalCargaDescarga,
    E.IndicadorFerroviaIntercambio,
    E.Wkt AS points,
    LE.Wkt AS lines,
    CAST(E.the_geom AS VARCHAR(MAX)) AS points_bin,
    CAST(LE.the_geom AS VARCHAR(MAX)) AS lines_bin

FROM [BD_SAFF].[dbo].[tblLinhaEstacao] LE

LEFT JOIN 
    [BD_SAFF].[dbo].[tblLinha] L
    ON LE.CodigoLinha = L.CodigoLinha
LEFT JOIN 
    [BD_SAFF].[dbo].[tblEstacao] E
    ON LE.CodigoEstacao = E.CodigoEstacao
LEFT JOIN 
    [BD_SAFF].[dbo].[tblFerrovia] F
    ON LE.CodigoFerrovia = F.CodigoFerrovia
LEFT JOIN
	[BD_SAFF].[dbo].[tblMunicipio] M
    ON E.CodigoMunicipio = M.CodigoMunicipio
LEFT JOIN
	[BD_SAFF].[dbo].[tblUF] UF
    ON M.CodigoUF = UF.CodigoUF
ORDER BY
    L.NomeLinha ASC,   -- Ordena por NomeLinha em ordem crescente
    LE.NumeroSequencia ASC; -- Em seguida, ordena por NumeroSequencia em ordem crescente