# API Esportiva — Comparação e Recomendação

## APIs Avaliadas

| Critério | API-Football | SportRadar | TheSportsDB | Football-Data.org |
|----------|-------------|------------|-------------|-------------------|
| Cobertura | 1000+ ligas | Elite ligas | Ampla | Europa foco |
| Ao vivo | ✅ | ✅ | ❌ | ✅ parcial |
| Estatísticas | ✅ completo | ✅ completo | ❌ básico | ✅ básico |
| Escanteios | ✅ | ✅ | ❌ | ❌ |
| Cartões | ✅ | ✅ | ❌ | ✅ |
| Odds | ✅ | ✅ | ❌ | ❌ |
| Histórico | ✅ profundo | ✅ profundo | ✅ | ✅ |
| Documentação | ✅ clara | ✅ excelente | ✅ | ✅ |
| Plano grátis | 100 req/dia | ❌ trial | ✅ | ✅ limitado |
| Custo | ~$15/mês | ~$500/mês | Grátis/Pro | Grátis/€20/mês |
| Estabilidade | Alta | Muito alta | Média | Alta |
| Ida e volta | ✅ detectável | ✅ | Parcial | Parcial |

---

## ✅ Recomendação: API-Football (RapidAPI)

**Por que foi escolhida:**

1. **Cobertura completa** das 5 regras: ao vivo, escanteios, cartões, odds, histórico detalhado
2. **Plano acessível** (~$15/mês) com 7500 req/dia — suficiente para monitoramento contínuo
3. **Endpoints para ida e volta**: `/fixtures` retorna `aggregate` e permite identificar `leg` automaticamente
4. **Documentação clara** e SDK não oficial disponível em Python
5. **Estabilidade** comprovada: usada em projetos de maior escala

**Endpoints principais para este projeto:**

```
GET /fixtures?live=all                  → partidas ao vivo
GET /fixtures?id={id}                   → detalhes + estatísticas
GET /fixtures/events?fixture={id}       → eventos (gols, cartões)
GET /fixtures/statistics?fixture={id}  → escanteios, posse, etc.
GET /odds?fixture={id}                 → odds em tempo real
GET /fixtures?team={id}&last=10        → histórico (Regra 4)
```

---

## Como Integrar

1. Cadastre-se em https://rapidapi.com/api-sports/api/api-football
2. Obtenha sua API Key
3. Edite `.env`:
   ```
   SPORTS_API_KEY=sua_chave_aqui
   SPORTS_API_PROVIDER=apifootball
   ```
4. Implemente `backend/providers/apifootball_provider.py` extendendo `SportsDataProvider`

A arquitetura `SportsDataProvider` garante que a troca de API não afeta o Rule Engine.

---

## ⚠️ Quando Integrar

**Não integre ainda.** O sistema funciona completamente com o `MockSportsProvider`.

Quando estiver pronto para dados reais, me informe e implemente o provider com sua API Key.
