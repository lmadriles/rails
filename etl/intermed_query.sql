WITH OrderedData AS (
    SELECT
        CONCAT(FER.SiglaFerrovia, FT.CodigoFluxoTransporteFerrovia) AS id,
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

SELECT * 
FROM ConcatenatedSiglas
ORDER BY id;