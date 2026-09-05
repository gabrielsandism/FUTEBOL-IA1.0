# Documentação das Regras

## Filosofia

Cada regra é uma hipótese estatística desenvolvida por observação.
O sistema detecta o cenário e registra — nunca afirma que algo irá acontecer.

Cada ocorrência registra:
- Quantidade de ocorrências
- Taxa histórica
- Tamanho da amostra
- Contexto da partida (minuto, placar, liga, times)

---

## RULE_001 — Sem Cartões Após 3x0

**Categoria:** Cartões  
**Prioridade:** 7/10  
**Versão:** 1.0.0

**Hipótese:** Em ligas importantes (primeira divisão) com times de elite, quando um time abre 3x0, existe tendência de não receber mais cartões.

**Condições de disparo:**
- Liga marcada como importante
- Primeira divisão
- Time leading deve ser elite
- Diferença de gols ≥ 3
- Gols do time líder ≥ 3

**Parâmetros configuráveis:**
| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| min_goal_diff | 3 | Diferença mínima de gols |
| leading_score_min | 3 | Mínimo de gols do líder |
| require_elite_team | true | Exige time de elite |
| require_important_league | true | Exige liga importante |
| require_first_division | true | Exige primeira divisão |

---

## RULE_002 — Sem Gol Primeiros 10min (Volta)

**Categoria:** Ida e Volta / Gols  
**Prioridade:** 6/10

**Hipótese:** Em competições com ida e volta, quando a ida termina com diferença de 1 gol, existe tendência de não ocorrer gol nos primeiros 10 minutos da volta.

**Condições:**
- Partida marcada como `leg_number=2`
- Contexto da ida disponível
- Diferença de gols da ida ≤ 1
- Minuto atual entre 1 e 10

**Parâmetros:**
| Parâmetro | Padrão |
|-----------|--------|
| max_first_leg_diff | 1 |
| monitoring_minutes | 10 |

---

## RULE_003 — Sem Cartões na Volta Após Goleada

**Categoria:** Ida e Volta / Cartões  
**Prioridade:** 6/10

**Hipótese:** Quando um time vence a ida por 4+ gols, existe tendência de não receber cartões na volta.

**Condições:**
- Partida de volta (`leg_number=2`)
- Diferença na ida ≥ 4 gols

---

## RULE_004 — Mais Escanteios Após Favorito Sofrer Gol

**Categoria:** Escanteios  
**Prioridade:** 7/10

**Hipótese:** Quando favorito joga em casa e sofre o primeiro gol, existe tendência de produzir mais escanteios.

**Filtros históricos aplicados:**
- Média de escanteios em casa (últimos 5 jogos)
- Média de escanteios em casa (últimos 10 jogos)
- Ambos configuráveis

**Parâmetros:**
| Parâmetro | Padrão |
|-----------|--------|
| max_home_odds | 2.0 |
| min_home_corners_avg_last5 | 4.0 |
| min_home_corners_avg_last10 | 4.0 |
| use_historical_filter | true |
| max_trigger_minute | 80 |

---

## RULE_005 — Virada Após Vermelho (Favorito em Casa)

**Categoria:** Virada  
**Prioridade:** 9/10 (máxima)

**Hipótese:** Quando favorito joga em casa, sofre o primeiro gol e o adversário recebe cartão vermelho, existe tendência de virada.

**Sequência obrigatória:**
1. Favorito em casa (odds ≤ 2.0 ou favorite_side=home)
2. Adversário marca primeiro gol
3. Adversário recebe cartão vermelho (após o gol)
4. Favorito ainda está perdendo no momento da avaliação

**Registros:**
- Minuto do gol
- Minuto do cartão vermelho
- Placar no momento
- (Pós-jogo) Resultado final e se houve virada

---

## Como Adicionar Novas Regras

1. Crie `backend/core/rules/rule_006.py` extendendo `BaseRule`
2. Defina `RULE_CODE`, `RULE_NAME`, `CATEGORY`, `PRIORITY`, `VERSION`
3. Implemente `evaluate(ctx: MatchContext) -> Optional[RuleResult]`
4. Registre em `backend/core/engine/rule_engine.py`:
   ```python
   from backend.core.rules.rule_006 import Rule006MinhaNovaRegra
   self.register(Rule006MinhaNovaRegra())
   ```
5. Adicione testes em `tests/unit/test_rules.py`
