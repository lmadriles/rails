/****** Script do comando SelectTopNRows de SSMS  ******/
SELECT
FER.SiglaFerrovia AS 'Ferrovia' 
, PESJU.RazaoSocial AS 'Cliente'
, MER.NomeMercadoria AS 'Mercadoria ANTT'
,(SELECT TOP (1) [NomeMercadoriaFerrovia]
	  FROM [BD_SAFF].[dbo].[tblMercadoriaFerrovia]
		where CodigoMercadoriaANTT = MER.CodigoMercadoria AND CodigoFerrovia = FER.CodigoFerrovia
		order by CodigoMercadoriaFerrovia asc)  AS 'Mercadoria Ferrovia'
, UT.SiglaUnidadeTarifaria AS 'Un. Tarifária'
, FT.[CodigoFluxoTransporteFerrovia] AS 'Código'
, FTT.NumeroSequencia AS 'sequencia_malha'
, FERF.SiglaFerrovia AS 'Ferrovia Trecho' 
, FTI.Sequencia AS 'sequencia_linha'
, LIN.NomeLinha AS 'Linha'
, EST_O.NomeEstacao AS 'Origem'
, EST_O.[CodigoTresLetrasEstacao] AS 'Origem Sigla'
,EST_D.NomeEstacao AS 'Destino'
, EST_D.[CodigoTresLetrasEstacao] AS 'Destino Sigla'
,FTI.DistanciaItinerario AS 'Distância (km)'
--,FER.*
  FROM [BD_SAFF].[dbo].[tblFluxoTransporteTrechoItinerario] FTI
  LEFT JOIN [BD_SAFF].[dbo].[tblEstacao] EST_O on EST_O.CodigoEstacao = FTI.CodigoEstacaoDe
  LEFT JOIN [BD_SAFF].[dbo].[tblEstacao] EST_D on EST_D.CodigoEstacao = FTI.CodigoEstacaoPara
  LEFT JOIN [BD_SAFF].[dbo].[tblLinha] LIN on LIN.CodigoLinha = FTI.CodigoLinha
  LEFT JOIN [BD_SAFF].[dbo].[tblFerrovia] FERF on FERF.CodigoFerrovia = LIN.CodigoFerrovia
  LEFT JOIN [BD_SAFF].[dbo].[tblFluxoTransporte] FT on FT.CodigoFluxoTransporte = FTI.CodigoFluxoTransporte 
  LEFT JOIN [BD_SAFF].[dbo].[tblFluxoTransporteTrecho] FTT on FTT.CodigoFluxoTransporteTrecho = FTI.CodigoFluxoTransporteTrecho
  LEFT JOIN [BD_SAFF].[dbo].[tblFerrovia] FER on FER.CodigoFerrovia = FT.CodigoFerrovia
  LEFT JOIN [BD_SAFF].[dbo].[tblCliente] CLI on CLI.CodigoCliente = FT.CodigoCliente
  LEFT JOIN [BD_SAFF].[dbo].[tblPessoaJuridica] PESJU on PESJU.CodigoPessoaJuridica = CLI.CodigoPessoa
  LEFT JOIN [BD_SAFF].[dbo].[tblMercadoria] MER on MER.CodigoMercadoria = FT.CodigoMercadoria
  LEFT JOIN [BD_SAFF].[dbo].[tblUnidadeTarifaria] UT on UT.CodigoUnidadeTarifaria = FT.CodigoUnidadeTarifaria
order by FER.SiglaFerrovia, FT.[CodigoFluxoTransporteFerrovia], FTT.NumeroSequencia, FTI.Sequencia