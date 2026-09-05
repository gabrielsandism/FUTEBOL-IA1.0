# 🚀 Football Scanner AI - Guia de Instalação Completo (Windows)

## PASSO 1: Baixar o Projeto

1. Vá para a pasta onde quer salvar o projeto
2. Baixe o arquivo `football_scanner_ai.zip`
3. Clique direito → **Extrair Tudo**
4. Escolha a pasta de destino e clique em **Extrair**

**Resultado:** Você terá uma pasta `football_scanner_ai/` com tudo dentro.

---

## PASSO 2: Verificar se Python está Instalado

1. Abra o **Prompt de Comando (CMD)** (não PowerShell)
   - Clique em Iniciar
   - Digite `cmd`
   - Pressione Enter

2. Cole este comando:
```
python --version
```

**Se aparecer** `Python 3.x.x`:
- ✅ Você tem Python instalado e pode seguir

**Se aparecer erro** `python não é reconhecido`:
- ❌ Você precisa instalar Python

### Instalando Python (se necessário)

1. Acesse: https://www.python.org/downloads/
2. Clique em **"Download Python 3.12"** (versão mais recente)
3. Na hora de instalar, **MARQUE A CAIXA** "Add Python to PATH"
4. Clique em **Install Now**
5. Espere terminar
6. Reinicie o computador
7. Abra CMD de novo e teste: `python --version`

---

## PASSO 3: Verificar se Node.js está Instalado

1. No CMD, cole:
```
node --version
```

**Se aparecer** `v18.x.x` ou superior:
- ✅ Você tem Node.js instalado e pode seguir

**Se aparecer erro**:
- ❌ Você precisa instalar Node.js

### Instalando Node.js (se necessário)

1. Acesse: https://nodejs.org/
2. Clique em **LTS** (versão recomendada)
3. Execute o instalador `.msi`
4. Marque **"Automatically install necessary tools"**
5. Clique em **Install**
6. Reinicie o computador
7. Abra CMD e teste: `node --version`

---

## PASSO 4: Instalar Dependências do Backend (Python)

1. Abra **Prompt de Comando**
2. Navegue até a pasta do projeto:

```cmd
cd C:\caminho\para\football_scanner_ai
```

(Substitua `C:\caminho\para\` pelo caminho real onde você extraiu)

3. Digite este comando:

```cmd
pip install -r requirements.txt
```

Isso vai instalar todas as bibliotecas Python necesárias. **Espere terminar** (pode levar 1-2 minutos).

---

## PASSO 5: Instalar Dependências do Frontend (Node)

1. No mesmo CMD, navegue até a pasta do frontend:

```cmd
cd frontend-react
```

2. Digite:

```cmd
npm install
```

Isso vai instalar todas as dependências do React. **Espere terminar** (pode levar 2-3 minutos).

---

## PASSO 6: Configurar o Arquivo .env

1. Na pasta raiz do projeto, abra o arquivo `.env` com um editor de texto
2. Verifique se está assim:

```env
DB_MODE=sqlite
SQLITE_PATH=./data/football_scanner.db
SPORTS_API_KEY=3321eeee21b24ff58d0a46bc86f6d2e0
SPORTS_API_PROVIDER=footballdata
APP_HOST=127.0.0.1
APP_PORT=8000
APP_DEBUG=false
LOG_LEVEL=INFO
RULE_ENGINE_INTERVAL=60
ALERT_RETENTION_HOURS=24
```

3. Salve o arquivo (Ctrl+S)

---

## PASSO 7: Abrir Dois CMDs (Terminal)

Você precisará abrir **DUAS** janelas de Prompt de Comando:

### Terminal 1 (Backend)
- Abra um novo CMD
- Navegue até a pasta do projeto:
```cmd
cd C:\caminho\para\football_scanner_ai
```

### Terminal 2 (Frontend)
- Abra OUTRO CMD
- Navegue até a pasta do frontend:
```cmd
cd C:\caminho\para\football_scanner_ai\frontend-react
```

**Organize as duas janelas lado a lado na tela** (ou use Alt+Tab para alternar).

---

## PASSO 8: Iniciar o Backend (Terminal 1)

No **Terminal 1**, digite:

```cmd
python launcher.py
```

Você vai ver:

```
============================================================
  ⚽  Football Scanner AI  v1.0.0
============================================================
  Modo DB   : SQLITE
  Provider  : footballdata
  Endereço  : http://127.0.0.1:8000
============================================================
  Pressione Ctrl+C para encerrar

INFO:     Started server process
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**NÃO FECHE ESTE TERMINAL.** Deixe rodando.

✅ Backend está online em: **http://127.0.0.1:8000**

---

## PASSO 9: Iniciar o Frontend (Terminal 2)

No **Terminal 2**, digite:

```cmd
npm run dev
```

Você vai ver:

```
  ▲ Next.js 14.1.0
  - Local:        http://localhost:3000
  - Environments: .env.local

 ✓ Ready in 2.1s
```

✅ Frontend está online em: **http://localhost:3000**

---

## PASSO 10: Acessar o Sistema

Abra seu navegador e acesse:

**http://localhost:3000**

Você verá:
- **Dashboard** com partidas ao vivo
- **Alertas** ativados em tempo real
- **Regras** que você pode ativar/desativar
- **Estatísticas** do sistema

---

## 🎉 Pronto!

O sistema está rodando!

### O que está acontecendo:

1. **Backend (Terminal 1)**: Busca dados da API football-data.org a cada 60 segundos
2. **Frontend (Terminal 2)**: Exibe os dados em tempo real no navegador
3. **Banco de dados**: Salvo em `./data/football_scanner.db` (SQLite portátil)

---

## Parar o Sistema

Para encerrar tudo:

1. No **Terminal 1** (Backend): Pressione `Ctrl+C`
2. No **Terminal 2** (Frontend): Pressione `Ctrl+C`
3. Feche os dois CMDs

---

## Erro Comum: vcruntime140.dll

Se aparecer erro sobre `vcruntime140.dll`:

1. Baixe: https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Execute o arquivo
3. Clique em "Instalar"
4. Reinicie o computador
5. Tente rodar de novo

---

## Próxima Vez

Quando quiser rodar o sistema novamente:

1. Abra **Terminal 1** na pasta raiz:
   ```cmd
   python launcher.py
   ```

2. Abra **Terminal 2** na pasta `frontend-react`:
   ```cmd
   npm run dev
   ```

3. Acesse: http://localhost:3000

**Nada de instalar novamente** — as dependências já estão instaladas!

---

## Troubleshooting

| Erro | Solução |
|------|---------|
| `python não é reconhecido` | Reinstale Python e marque "Add to PATH" |
| `npm não é reconhecido` | Reinstale Node.js |
| `pip install falha` | Tente: `python -m pip install -r requirements.txt` |
| `Porta 8000 em uso` | Mude em `.env`: `APP_PORT=8001` |
| `Porta 3000 em uso` | Mude em `frontend-react/.env.local`: `PORT=3001` |
| `API não conecta` | Verifique internet e a chave em `.env` |

---

## 📞 Precisa de Ajuda?

Se algo não funcionar:

1. Verifique se Python e Node.js estão instalados corretamente
2. Verifique se você está na pasta certa
3. Tente fechar e abrir os terminais novamente
4. Reinicie o computador

🎯 **Seu sistema Football Scanner AI está pronto!**
