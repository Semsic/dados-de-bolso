# Dados de Bolso

Uma lupa de terminal para arquivos CSV. Mostra tamanho, colunas, valores vazios, duplicatas e uma estimativa simples dos tipos — sem instalar uma procissão de dependências.

## Requisitos

Python 3.10 ou mais recente. Só usa a biblioteca padrão.

## Instalação local

```bash
python -m pip install .
```

## Uso

```bash
dados-de-bolso clientes.csv
dados-de-bolso vendas.csv --json
dados-de-bolso dados.csv --delimiter ';' --encoding latin-1
```

O separador é detectado automaticamente quando possível. `--json` gera um relatório para salvar ou encaminhar a outro programa; os valores das células não são incluídos no relatório.

### Regras de saída

- Código `0`: arquivo lido e analisado.
- Código `1`: erro ao abrir ou interpretar o arquivo.
- Código `2`: argumentos inválidos.

## Limites conhecidos

É uma ferramenta de inspeção rápida, não um validador formal de qualidade de dados. A inferência de tipos é conservadora: colunas ambíguas ficam como texto. Arquivos muito grandes podem levar um tempo porque a contagem de duplicatas considera as linhas completas.

## Licença

MIT. Consulte [LICENSE](LICENSE).
