# YouTube → MP3

App de desktop (PyQt6) para baixar vídeos, músicas ou playlists do YouTube e
converter para MP3.

## Funcionalidades

- Aceita links de vídeo único, música ou playlist, inclusive vários de uma vez
  (um por linha).
- Playlists e múltiplos links são expandidos em uma lista única de faixas
  para confirmação antes do download.
- Cada faixa pode ser marcada/desmarcada individualmente.
- Clique no título de uma faixa para renomear o arquivo final.
- Escolha da pasta de destino antes de baixar.
- Progresso individual por faixa e progresso geral do download.

## Requisitos

- Python 3.10+
- [ffmpeg](https://ffmpeg.org/) instalado e disponível no `PATH` (necessário
  para converter o áudio para MP3)

Instalar o ffmpeg:

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS (Homebrew)
brew install ffmpeg

# Windows (Chocolatey)
choco install ffmpeg
```

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

```bash
source .venv/bin/activate
python main.py
```

1. Cole um ou mais links (vídeo, música ou playlist) na caixa de texto, um
   por linha.
2. Clique em **Buscar links**. As faixas encontradas aparecem na lista com
   caixas de seleção.
3. Desmarque o que não quiser baixar. Clique no título de uma faixa para
   renomear o arquivo de saída.
4. Clique em **Escolher pasta de destino** para definir onde os MP3s serão
   salvos.
5. Clique em **Baixar selecionados** e acompanhe o progresso na tabela e na
   barra inferior.
