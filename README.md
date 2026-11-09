# Rastreador de hábitos

Registre seus hábitos pelo terminal e acompanhe a frequência e as sequências de dias consecutivos.

## Requisitos

- Python 3.9 ou superior

## Começar

```bash
python3 habit_tracker.py log Leitura
python3 habit_tracker.py log Exercício
python3 habit_tracker.py history
python3 habit_tracker.py summary
```

Uma data pode ser informada no formato `AAAA-MM-DD`:

```bash
python3 habit_tracker.py log Leitura --date 2025-01-15
```

Os registros são guardados no arquivo `habits.json` do diretório atual. Use `--file caminho/arquivo.json` para escolher outro arquivo.

## Testes

```bash
python3 -m unittest discover -s tests -v
```

## O que este projeto pratica

Validação de datas, persistência JSON, interface de linha de comando e cálculo de sequências de dias com funções testáveis.
