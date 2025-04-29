# Projeto de Malha Ferroviária e Roteamento de Fluxos

Este projeto é uma solução para integração de bases de dados e implementação de modelos de malha ferroviária. Ele realiza o roteamento de cada fluxo sobre a malha e permite a aplicação de filtros baseados nas rotas traçadas. O objetivo é subsidiar análises e relatórios para acompanhamento da produção ferroviária em cada segmento.

## Funcionalidades

1. **Integração de Bases de Dados**: Reúne diversas fontes de dados para gerar uma representação consistente da malha ferroviária.
2. **Modelo de Malha Ferroviária**: Define a estrutura da malha ferroviária para simulações e análises.
3. **Roteamento de Fluxos**: Permite calcular rotas otimizadas sobre a malha ferroviária.
4. **Filtragem de Fluxos**: Aplica filtros a fluxos baseados nos trajetos realizados.

## Configuração do Ambiente

O projeto utiliza o [Poetry](https://python-poetry.org/) para gerenciar dependências e o ambiente virtual. Certifique-se de ter o Poetry instalado antes de prosseguir.

### Instruções de Instalação

1. Clone este repositório:
   ```bash
   git clone https://github.com/lmadriles/rails.git
   cd <nome-do-repositorio>
   ```

2. Instale as dependências:
   ```bash
   poetry install
   ```

3. Ative o ambiente virtual:
   ```bash
   poetry shell
   ```

## Uso do Projeto

Os scripts principais do projeto podem ser executados diretamente pelo terminal usando o comando `python -m` (execução de módulo). Aqui estão alguns exemplos:

### 1. Integração de Bases de Dados
Executa o script de integração de dados:
```bash
python -m etl
```

### 2. Modelo de Malha Ferroviária e Roteamento dos Fluxos
Gera e valida o modelo da malha ferroviária:
```bash
python -m routes
```

## Estrutura do Projeto

```
rails/
├── data
│   ├── final
│   ├── processed
│   ├── raw
├── etl        # extração, transformação e carregamento dos dados
├── routes     # criação da informação de rotas
├── utils      # funções auxiliares
├── .python-version
├── poetry.lock
├── pyproject.toml
└── README.md
```

## Contribuição

1. Faça um fork deste repositório.
2. Crie um branch para sua funcionalidade ou correção:
   ```bash
   git checkout -b minha-nova-funcionalidade
   ```
3. Envie suas modificações:
   ```bash
   git push origin minha-nova-funcionalidade
   ```
4. Abra um Pull Request.


