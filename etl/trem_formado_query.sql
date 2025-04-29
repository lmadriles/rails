SELECT

	TF.DataReferencia,
	F.SiglaFerrovia,
	EF.CodigoTresLetrasEstacao AS EstacaoFormacao,
	EE.CodigoTresLetrasEstacao AS EstacaoEncerramento,
	TF.Prefixo,
	CAST(TF.NumeroTrensFormados AS INT) AS NumeroTrensFormados,
	CAST(TF.NumeroLocomotivas AS INT) AS NumeroLocomotivas,
	CAST(TF.NumeroVagoesCarregados AS INT) AS NumeroVagoesCarregados,
	CAST(TF.NumeroVagoesVazios AS INT) AS NumeroVagoesVazios,
	CAST(TF.ValorTU AS REAL) AS ValorTU,
	CAST(TF.Comprimento AS REAL) AS Comprimento,
	CAST(TF.TempoViagem AS REAL) AS TempoViagem,
	CAST(TF.Distancia AS REAL) AS Distancia,
	TF.IndicadorFuncaoCarga,
	TF.IndicadorFuncaoPassageiro,
	TF.IndicadorFuncaoServico,
	CAST(TF.NumeroTempoTotalMarcha AS REAL) AS NumeroTempoTotalMarcha,
	CAST(TF.NumeroTempoTotalParado AS REAL) AS NumeroTempoTotalParado,
	TF.DataFormacao,
	TF.DataEncerramento,
	FP.SiglaFerrovia AS FerroviaPercorida,
	E1.CodigoTresLetrasEstacao AS Inter1,
	E2.CodigoTresLetrasEstacao AS Inter2,
	E3.CodigoTresLetrasEstacao AS Inter3,
	E4.CodigoTresLetrasEstacao AS Inter4,
	MF.NomeMercadoriaFerrovia,
	M.NomeMercadoria

FROM [BD_SAFF].[dbo].[tblTremFormado] TF

LEFT JOIN [BD_SAFF].[dbo].[tblEstacao] EF
	ON TF.CodigoEstacaoFormacao = EF.CodigoEstacao

LEFT JOIN [BD_SAFF].[dbo].[tblEstacao] EE
	ON TF.CodigoEstacaoEncerramento = EE.CodigoEstacao

LEFT JOIN [BD_SAFF].[dbo].[tblFerrovia] F
	ON TF.CodigoFerrovia = F.CodigoFerrovia

LEFT JOIN [BD_SAFF].[dbo].[tblFerrovia] FP
	ON TF.CodigoFerroviaPercorrida = FP.CodigoFerrovia

LEFT JOIN [BD_SAFF].[dbo].[tblEstacao] E1
	ON TF.CodigoEstacaoInter1 = E1.CodigoEstacao

LEFT JOIN [BD_SAFF].[dbo].[tblEstacao] E2
	ON TF.CodigoEstacaoInter2 = E2.CodigoEstacao

LEFT JOIN [BD_SAFF].[dbo].[tblEstacao] E3
	ON TF.CodigoEstacaoInter3 = E3.CodigoEstacao

LEFT JOIN [BD_SAFF].[dbo].[tblEstacao] E4
	ON TF.CodigoEstacaoInter4 = E4.CodigoEstacao

LEFT JOIN [BD_SAFF].[dbo].[tblTremFormadoMercadoria] TFM
	ON TF.CodigoTremFormado = TFM.CodigoTremFormado

LEFT JOIN [BD_SAFF].[dbo].[tblMercadoriaFerrovia] MF
	ON TFM.CodigoMercadoriaFerrovia = MF.CodigoMercadoriaFerrovia

LEFT JOIN [BD_SAFF].[dbo].[tblMercadoria] M
	ON MF.CodigoMercadoriaANTT = M.CodigoMercadoria

WHERE TF.DataReferencia > '2019-12-31'