WITH fluxos AS (

	SELECT
		CAST(FT.CodigoFluxoTransporteFerrovia AS NVARCHAR) + F.SiglaFerrovia AS id,
		FT.CodigoFluxoTransporte,
		FT.CodigoFluxoTransporteFerrovia,
		F.SiglaFerrovia,
		PJ.RazaoSocial,
		M.NomeMercadoria,
		CAST(FT.DistanciaItinerario AS REAL) AS DistanciaItinerario,
		FT.CodigoReferenciaEstacaoOrigem,
		FT.CodigoReferenciaEstacaoDestino,
		EO.CodigoTresLetrasEstacao AS Origem,
		ED.CodigoTresLetrasEstacao AS Destino

	FROM [BD_SAFF].[dbo].[tblFluxoTransporte] FT

	INNER JOIN [BD_SAFF].[dbo].[tblEstacao] EO
		ON FT.CodigoEstacaoOrigem = EO.CodigoEstacao

	INNER JOIN [BD_SAFF].[dbo].[tblEstacao] ED
		ON FT.CodigoEstacaoDestino = ED.CodigoEstacao

	INNER JOIN [BD_SAFF].[dbo].[tblFerrovia] F
		ON FT.CodigoFerrovia = F.CodigoFerrovia

	INNER JOIN [BD_SAFF].[dbo].[tblMercadoria] M 
		ON FT.CodigoMercadoria = M.CodigoMercadoria

	INNER JOIN [BD_SAFF].[dbo].[tblCliente] C
		ON FT.CodigoCliente = C.CodigoCliente

	INNER JOIN [BD_SAFF].[dbo].[tblPessoaJuridica] PJ
		ON C.CodigoPessoa = PJ.CodigoPessoaJuridica

)

SELECT
    FTR.DataReferencia,
	fluxos.*,
    CAST(FTR.ValorTU AS REAL) AS ValorTU,
    CAST(FTR.ValorTKU AS REAL) AS ValorTKU,
	CAST(FTR.NumeroCarregamentos AS INT) AS NumeroCarregamentos

FROM [BD_SAFF].[dbo].[tblFluxoTransporteRealizado] FTR

INNER JOIN fluxos
    ON FTR.CodigoFluxoTransporte = fluxos.CodigoFluxoTransporte;
