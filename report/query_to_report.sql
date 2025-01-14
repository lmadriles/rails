SELECT 
    o.data,
    o.id,
    o.TU,
    o.ValorTKU,
    f.ferrovia,
    f.cliente,
    f.mercadoria,
    f.origem,
    f.destino,
    f.dist_media,
    f.intermed,
    f.len_Dijkstra,
    f.rota
FROM 
    ocorrencias o
LEFT JOIN 
    fluxos_rotas_2017 f
ON 
    o.id = f.id
WHERE 
    o.data >= '2024-01-01' and o.data <= '2024-12-01';
