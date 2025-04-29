WITH OrderedData AS (
    SELECT
        CONCAT(FT.CodigoFluxoTransporteFerrovia, FER.SiglaFerrovia) AS id,
        FTT.NumeroSequencia,
        FTI.Sequencia,
        EST_O.CodigoTresLetrasEstacao AS Origem,
        EST_D.CodigoTresLetrasEstacao AS Destino,
        LAG(EST_D.CodigoTresLetrasEstacao) OVER (
            PARTITION BY CONCAT(FER.SiglaFerrovia, FT.CodigoFluxoTransporteFerrovia) 
            ORDER BY FTT.NumeroSequencia, FTI.Sequencia
        ) AS DestinoAnterior
    FROM 
        [BD_SAFF].[dbo].[tblFluxoTransporteTrechoItinerario] FTI
        LEFT JOIN [BD_SAFF].[dbo].[tblEstacao] EST_O ON EST_O.CodigoEstacao = FTI.CodigoEstacaoDe
        LEFT JOIN [BD_SAFF].[dbo].[tblEstacao] EST_D ON EST_D.CodigoEstacao = FTI.CodigoEstacaoPara
        LEFT JOIN [BD_SAFF].[dbo].[tblFluxoTransporte] FT ON FT.CodigoFluxoTransporte = FTI.CodigoFluxoTransporte 
        LEFT JOIN [BD_SAFF].[dbo].[tblFluxoTransporteTrecho] FTT ON FTT.CodigoFluxoTransporteTrecho = FTI.CodigoFluxoTransporteTrecho
        LEFT JOIN [BD_SAFF].[dbo].[tblFerrovia] FER ON FER.CodigoFerrovia = FT.CodigoFerrovia
),

ConcatenatedSiglas AS (
    SELECT
        id,
        STRING_AGG(CASE 
            WHEN DestinoAnterior = Origem THEN Destino
            ELSE Origem + ' ' + Destino 
        END, ' ') WITHIN GROUP (ORDER BY NumeroSequencia, Sequencia) AS concatenated_siglas
    FROM 
        OrderedData
    GROUP BY 
        id
)

SELECT
    CS.id,
    FT.CodigoFluxoTransporteFerrovia,
    F.SiglaFerrovia,
    PJ.RazaoSocial,
    M.NomeMercadoria,
    CAST(FT.DistanciaItinerario AS REAL) AS DistanciaItinerario,
    FT.CodigoReferenciaEstacaoOrigem,
    FT.CodigoReferenciaEstacaoDestino,
    EO.CodigoTresLetrasEstacao AS Origem,
    ED.CodigoTresLetrasEstacao AS Destino,
    CS.concatenated_siglas

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
LEFT JOIN ConcatenatedSiglas CS
    ON CONCAT(FT.CodigoFluxoTransporteFerrovia, F.SiglaFerrovia) = CS.id
ORDER BY FT.CodigoFluxoTransporte;
