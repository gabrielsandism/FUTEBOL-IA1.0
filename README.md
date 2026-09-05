# Football Scanner AI

Sistema de monitoramento e análise estatística de partidas de futebol em tempo real.

## Filosofia

> Métricas desenvolvidas observando futebol durante anos. O sistema identifica automaticamente quando essas métricas acontecem.

**O sistema não prevê resultados.** Detecta cenários estatísticos e registra ocorrências, taxas e contexto.

---

## Regras Implementadas

| Código | Nome | Categoria |
|--------|------|-----------|
| RULE_001 | Sem Cartões Após 3x0 | Cartões |
| RULE_002 | Sem Gol Primeiros 10min (Volta) | Ida e Volta |
| RULE_003 | Sem Cartões na Volta Após Goleada | Ida e Volta |
| RULE_004 | Mais Escanteios Após Favorito Sofrer Gol | Escanteios |
| RULE_005 | Virada Após Vermelho (Favorito em Casa) | Virada |

---

## Instalação Rápida

```bash
# 1. Clone ou extraia o projeto
cd football_scanner_ai

# 2. Instale dependências
pip install -r requirements.txt

# 3. Execute
python launcher.py
```

Acesse: http://127.0.0.1:8000

---

## Modos de Banco de Dados

### Modo Portable (SQLite) — padrão
```env
DB_MODE=sqlite
SQLITE_PATH=./data/football_scanner.db
```
- Funciona sem instalação adicional
- Ideal para pendrive e uso pessoal

### Modo Completo (PostgreSQL)
```env
DB_MODE=postgresql
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=football_scanner
POSTGRES_USER=postgres
POSTGRES_PASSWORD=senha
```

---

## Build Windows (.exe)

```bat
scripts\build_windows.bat
```

Resultado: `dist\FootballScannerAI\FootballScannerAI.exe`

Para versão portátil: copie toda a pasta `dist\FootballScannerAI\` para o pendrive.

---

## Integração com API Real

Ao chegar o momento de dados reais, edite `.env`:

```env
SPORTS_API_KEY=sua_chave_aqui
SPORTS_API_PROVIDER=apifootball   # após implementar o provider
```

O sistema usa a interface `SportsDataProvider` — troque o provider sem alterar o Rule Engine.

---

## Estrutura do Projeto

```
football_scanner_ai/
├── backend/
│   ├── api/routes/          # FastAPI routes
│   ├── core/
│   │   ├── engine/          # Rule Engine base
│   │   └── rules/           # As 5 regras
│   ├── db/models/           # SQLAlchemy models
│   ├── providers/           # SportsDataProvider interface
│   └── services/            # Monitor + Backtest
├── frontend/templates/      # HTML pages
├── config/                  # Settings (.env)
├── tests/                   # 58 testes automatizados
├── launcher.py              # Ponto de entrada
└── FootballScannerAI.spec   # PyInstaller config
```

---

## Testes

```bash
pytest tests/ -v
# 58 testes | 57 unitários + 1 integração
```

---

## Aviso

Todas as regras são hipóteses estatísticas. O sistema sempre registra:
- Quantidade de ocorrências
- Taxa histórica
- Tamanho da amostra
- Contexto da partida

**Nunca afirma que um evento irá acontecer.**
