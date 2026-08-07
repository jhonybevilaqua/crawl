# Sistema Crawl TV - Painel de Notícias e Cotações

Sistema web para buscar notícias via RSS, cotações de moedas e commodities, com sistema de aprovação e exportação em TXT para integração com sistema de GC (Graphics Controller) de emissora de TV.

## Funcionalidades

- **Feed RSS**: Busca manchetes de múltiplos feeds configuráveis
- **Cotações automáticas**: Dólar e Euro via AwesomeAPI; Commodities (Soja, Milho, Trigo, Boi) via Yahoo Finance
- **Cotações manuais**: Opção de inserir valores manualmente quando necessário
- **Aprovação de notícias**: Aprove ou rejeite cada manchete individualmente ou em lote
- **Exportação TXT**: Gera arquivo .txt com cotações e notícias aprovadas em formato sequencial (sem quebras de linha entre notícias, separadas por •)
- **Substituição automática**: O arquivo é sempre sobrescrito no caminho definido
- **Comparação de cotações**: Setas ▲ (subiu), ▼ (caiu), ■ (estável) comparado ao dia anterior

## Requisitos

- Python 3.8+
- pip

## Instalação

1. Extraia o arquivo ZIP em uma pasta
2. Abra o terminal na pasta do projeto
3. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Como usar

1. Inicie o servidor:

```bash
python app.py
```

2. Abra o navegador em: `http://localhost:5000`

3. Na aba **Configurações**, ajuste:
   - Feeds RSS que deseja monitorar
   - Caminho padrão de exportação do arquivo TXT

4. Na aba **Painel Principal**:
   - Clique em "Atualizar cotações" para buscar valores atuais
   - Clique em "Atualizar feed" para buscar notícias
   - Aprove (✓) ou rejeite (✕) as manchetes
   - Use os botões de toolbar para aprovar/rejeitar em lote
   - Defina o caminho do arquivo TXT e clique em "Exportar TXT"

## Formato do arquivo exportado

```
Dólar: R$ 5,85 ▲ | Euro: R$ 6,42 ▼ | Soja (saca 60kg): R$ 142,50 ▲ | Milho (saca 60kg): R$ 68,30 ■ | Trigo (saca 60kg): R$ 95,00 ▲ | Boi gordo (@): R$ 298,00 ▼

• Manchete aprovada 1 • Manchete aprovada 2 • Manchete aprovada 3
```

Todas as notícias aprovadas ficam em uma única linha sequencial, separadas por `•`.

## Integração com GC

Configure o caminho de exportação para a pasta que o sistema de GC da sua emissora monitora. Exemplo:

```
C:\GC\crawl\noticias_crawl.txt
```

A cada exportação, o arquivo anterior é substituído automaticamente.

## Cotações de Commodities

O sistema busca cotações agrícolas brasileiras via **web scraping do Notícias Agrícolas**, que espelha os indicadores oficiais do **CEPEA/ESALQ**:
- **Soja**: Indicador ESALQ/B3 - Paranaguá (R$/saca 60kg)
- **Milho**: Indicador ESALQ/B3 (R$/saca 60kg)
- **Trigo**: Indicador CEPEA - PR/RS (R$/saca 60kg, convertido de tonelada)
- **Boi**: Indicador CEPEA/ESALQ (R$/@)

> **Nota**: O scraping depende da estrutura do site Notícias Agrícolas. Se houver mudanças no site ou bloqueios, o sistema mostrará um aviso e usará o modo manual ou o último histórico disponível. Para garantir valores sempre atualizados, use o modo **manual** inserindo os dados do boletim CEPEA diariamente.

## Modo Manual de Cotações

Marque "Usar cotações manuais" para inserir valores próprios. Útil quando você tem acesso a cotações internas ou deseja usar valores do CEPEA/ESALQ.

## Estrutura de arquivos

```
sistema_crawl_tv/
├── app.py              # Servidor Flask
├── requirements.txt    # Dependências Python
├── config.json         # Configurações (feeds, caminho de exportação)
├── quotes_history.json # Histórico de cotações para comparação
└── templates/
    └── index.html      # Interface web
```

## Categorias de notícias

Cada feed RSS pode ser associado a uma categoria. O sistema vem pré-configurado com:
- **Economia** — G1 Economia
- **Política** — G1 Política
- **Agronegócio** — Canal Rural, Notícias Agrícolas
- **Ciência** — G1 Ciência e Saúde
- **Tecnologia** — G1 Tecnologia

Na interface principal, você verá botões de filtro acima da lista de notícias. Clique para ativar/desativar uma categoria. Apenas as categorias ativas serão buscadas.

Cada notícia exibe uma tag colorida indicando sua categoria, facilitando a visualização.

## Feeds RSS sugeridos

| Feed | URL | Categoria |
|---|---|---|
| G1 Economia | `https://g1.globo.com/rss/g1/economia/` | Economia |
| G1 Política | `https://g1.globo.com/rss/g1/politica/` | Política |
| Canal Rural | `https://www.canalrural.com.br/feed/` | Agronegócio |
| Notícias Agrícolas | `https://www.noticiasagricolas.com.br/rss.php` | Agronegócio |
| G1 Ciência | `https://g1.globo.com/rss/g1/ciencia-e-saude/` | Ciência |
| G1 Tecnologia | `https://g1.globo.com/rss/g1/tecnologia/` | Tecnologia |
| Valor Econômico | `https://valor.globo.com/rss.xml` | Economia |
| Agrolink | `https://www.agrolink.com.br/rss/noticias.xml` | Agronegócio |

## Solução de problemas

**As cotações não carregam?**
- Verifique sua conexão com a internet
- O Yahoo Finance pode ter limites de requisição; aguarde alguns minutos
- Use o modo manual como alternativa

**As notícias não aparecem?**
- Alguns feeds RSS podem estar indisponíveis temporariamente
- Verifique se a URL do feed está correta na aba Configurações

**Erro de permissão ao exportar?**
- Certifique-se de que a pasta de destino existe
- Execute o terminal como administrador se necessário
- Verifique se o caminho está correto (use `\\` no Windows)



---



---

## Como rodar no macOS

### Opção 1: Executar diretamente pelo Terminal (recomendado)

1. Extraia o ZIP em uma pasta
2. Abra o **Terminal** e navegue até a pasta:
```bash
cd ~/Downloads/sistema_crawl_tv
```
3. Execute o script:
```bash
chmod +x run.sh
./run.sh
```
Ou, se preferir, rode diretamente:
```bash
pip3 install -r requirements.txt
python3 app.py
```
4. O navegador abrirá automaticamente em `http://localhost:5000`

### Opção 2: Criar app bundle (.app)

Se quiser um ícone no Dock como qualquer outro app:

```bash
chmod +x build_mac.sh
./build_mac.sh
```

Isso cria um arquivo `.app` dentro da pasta `dist/`. Você pode arrastar para a pasta **Aplicativos**.

> **Nota:** A primeira execução pode exigir que você vá em **Preferências do Sistema > Segurança e Privacidade** e clique em "Abrir mesmo assim", pois o app não está assinado pela Apple.

### Solução de problemas no Mac

**"pip3 não encontrado"**
```bash
# Instale o Homebrew primeiro
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
# Depois instale o Python
brew install python3
```

**"Permissão negada ao executar run.sh"**
```bash
chmod +x run.sh
```

**"O app não abre — desenvolvedor não verificado"**
- Clique com o botão direito no app → **Abrir**
- Ou vá em **Preferências do Sistema > Segurança e Privacidade > Geral** e clique em **Abrir mesmo assim**

## Como criar o executável Windows (.exe)

Se você quer distribuir o sistema como um único arquivo executável, sem precisar instalar Python na máquina, siga os passos abaixo.

### Pré-requisitos

- Windows 10/11
- Python 3.8+ instalado (marque "Add to PATH" na instalação)

### Passo a passo

#### Opção 1: Script automático (recomendado)

1. Extraia o ZIP do projeto em uma pasta
2. Abra a pasta e **clique duplo em `build.bat`**
3. Aguarde a compilação (pode levar 2-5 minutos)
4. O executável será gerado em `dist\SistemaCrawlTV.exe`

#### Opção 2: Linha de comando manual

```bash
# 1. Navegue até a pasta do projeto
cd sistema_crawl_tv

# 2. Instale dependências
pip install -r requirements.txt
pip install pyinstaller

# 3. Execute o build
python build.py
```

O executável será gerado em `dist\SistemaCrawlTV.exe`.

### O que o executável faz?

- **Um único arquivo** `.exe` (~15-30 MB) com tudo incluso
- **Não precisa de Python** instalado na máquina
- **Abre o navegador automaticamente** ao iniciar
- **Roda em segundo plano** (sem janela de terminal)
- **Para encerrar**: feche a janela do navegador ou use o Gerenciador de Tarefas

### Distribuição

Para distribuir para outras máquinas:

1. Copie a pasta `dist\` inteira (ou apenas o `.exe` se for `--onefile`)
2. Cole na máquina de destino
3. Clique duplo em `SistemaCrawlTV.exe`
4. O navegador abre automaticamente em `http://localhost:5000`

> **Importante**: O executável precisa de conexão com a internet para buscar RSS e cotações. O arquivo TXT de exportação é salvo localmente no caminho configurado.

### Solução de problemas no build

**"pip não é reconhecido"**
- Reinstale o Python marcando "Add Python to PATH"

**"PyInstaller não encontrado"**
```bash
pip install --upgrade pyinstaller
```

**"Arquivo muito grande"**
- Isso é normal. O PyInstaller empacota o Python runtime inteiro (~15-25 MB)
- Use `--onefile` para um único .exe ou remova `--onefile` para uma pasta com arquivos menores

**"Antivírus detecta como suspeito"**
- Isso é comum com PyInstaller. Adicione o arquivo às exceções do antivírus
- Ou use `--onedir` em vez de `--onefile`



---

## Como hospedar online GRÁTIS no Render.com (guia passo a passo)

O [Render.com](https://render.com) é um serviço de hospedagem na nuvem que oferece plano **gratuito** para aplicações web. Com ele, você sobe o CRAWL TV EVANGELIZAR para a internet e acessa de qualquer lugar — sem precisar deixar uma máquina ligada na emissora.

> **Importante:** o plano free "dorme" após 15 minutos de inatividade. A primeira pessoa que acessar demora ~30 segundos para "acordar". Para uso contínuo em emissora, considere o plano pago (US$ 7/mês) ou use uma máquina local como servidor.

---

### Passo 1: Crie uma conta no Render

1. Acesse [https://render.com](https://render.com)
2. Clique em **"Get Started for Free"**
3. Cadastre-se com sua conta do **GitHub** (recomendado) ou email

---

### Passo 2: Crie um repositório no GitHub

O Render precisa que seu código esteja no GitHub para fazer o deploy automático.

1. Acesse [https://github.com](https://github.com) e faça login
2. Clique no botão **"+"** (canto superior direito) → **"New repository"**
3. Nomeie como `crawl-tv-evangelizar`
4. Deixe como **Public** (ou Private se tiver conta paga no GitHub)
5. Clique em **"Create repository"**

---

### Passo 3: Envie o código para o GitHub

Na pasta do projeto no seu computador, abra o terminal e execute:

```bash
# Navegue até a pasta do projeto
cd sistema_crawl_tv

# Inicializa o Git
git init

# Adiciona todos os arquivos
git add .

# Faz o primeiro commit
git commit -m "Primeira versao do CRAWL TV EVANGELIZAR"

# Conecta com o repositorio do GitHub (substitua SEU_USUARIO pelo seu nome no GitHub)
git remote add origin https://github.com/SEU_USUARIO/crawl-tv-evangelizar.git

# Envia o codigo
git push -u origin main
```

> Se der erro no `git push`, tente `git branch -M main` antes do push.

---

### Passo 4: Conecte o Render ao GitHub

1. Volte ao [Render.com](https://render.com) e faça login
2. No dashboard, clique em **"New +"** → **"Web Service"**
3. Escolha **"Build and deploy from a Git repository"**
4. Clique em **"Connect account"** e autorize o Render a acessar seu GitHub
5. Selecione o repositório `crawl-tv-evangelizar`
6. Clique em **"Connect"**

---

### Passo 5: Configure o deploy

Na tela de configuração, preencha:

| Campo | Valor |
|---|---|
| **Name** | `crawl-tv-evangelizar` (ou o nome que quiser) |
| **Region** | `Oregon (US West)` (mais próximo do Brasil) |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn -k eventlet -w 1 app:app --bind 0.0.0.0:$PORT` |

> **NÃO altere** os arquivos `render.yaml` e `Procfile` que já estão no projeto — eles já têm essa configuração.

Clique em **"Create Web Service"**.

---

### Passo 6: Aguarde o deploy

O Render vai:
1. Baixar seu código do GitHub
2. Instalar as dependências (`requirements.txt`)
3. Compilar e iniciar o servidor

Isso leva **2-5 minutos** na primeira vez. Você verá os logs em tempo real.

Quando aparecer **"Your service is live"**, anote o link — algo como:
```
https://crawl-tv-evangelizar.onrender.com
```

---

### Passo 7: Acesse de qualquer lugar

Abra o navegador e acesse o link gerado pelo Render. Pronto! O sistema está online.

Você pode:
- Acessar do celular, tablet, outro computador
- Compartilhar o link com a equipe da emissora
- Usar em qualquer lugar com internet

---

### Passo 8: Atualizar o código (deploy automático)

Sempre que você fizer uma alteração no código e enviar para o GitHub, o Render **recompila automaticamente**:

```bash
# Na pasta do projeto, depois de editar algo:
git add .
git commit -m "Descricao da mudanca"
git push origin main
```

O Render detecta o push e faz o deploy novo em ~2 minutos.

---

### Solução de problemas no Render

**"Build failed"**
- Verifique se o `requirements.txt` está correto
- Confira se o `app.py` está na raiz do projeto

**"Service sleeping"**
- Normal no plano free. A primeira visita após 15 min de inatividade demora ~30s
- Para evitar isso, use o plano **Starter** (US$ 7/mês) ou acesse periodicamente

**"Application error"**
- Clique em **"Logs"** no dashboard do Render para ver o erro
- Geralmente é alguma dependência faltando no `requirements.txt`

**Quero usar domínio próprio (ex: crawl.minhaemissora.com.br)**
- No dashboard do Render, vá em **Settings** → **Custom Domains**
- Siga as instruções para configurar o DNS
- Funciona no plano free também

---

### Resumo dos custos

| Plano | Custo | O que inclui |
|---|---|---|
| **Free** | US$ 0 | App "dorme" após 15min inativo. 512MB RAM. |
| **Starter** | US$ 7/mês | App online 24h. 512MB RAM. |
| **Standard** | US$ 25/mês | App online 24h. 2GB RAM. |

Para uma emissora de TV, o plano **Starter (US$ 7/mês)** é suficiente e resolve o problema do "sleeping".

## Licença

Uso interno livre para emissoras de TV.
