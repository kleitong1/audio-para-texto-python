# Download do executável
Nesse [link](https://mega.nz/file/dkpWVCxZ#d2tAbnU-uMFmZVCBO-UP8VsKAPPm1M8X2z9xSqX1FEE) eu disponibilizei para baixa-lo e utililizar no Windows.

# Transcritor de Áudio do Alequinho

## Descrição
Este é um aplicativo para transcrição de áudio que utiliza a biblioteca `SpeechRecognition` para converter arquivos de áudio em texto. O aplicativo permite que o usuário selecione um arquivo de áudio (`.mp3`, `.wav`, `.flac`), o converta para o formato `.wav` (se necessário) e faça a transcrição utilizando a API de reconhecimento de voz do Google.

A interface gráfica foi criada usando `Tkinter` para proporcionar uma experiência amigável ao usuário.

---

## Funcionalidades
- Selecionar um arquivo de áudio.
- Conversão automática para o formato `.wav`, caso necessário.
- Transcrição do áudio em segmentos de 1 minuto.
- Barra de progresso para acompanhar o progresso da transcrição.
- Salvar a transcrição em um arquivo `.txt` no diretório desejado ou na pasta padrão `transcricoes`.

---

## Requisitos

Certifique-se de ter as seguintes dependências instaladas no ambiente:

- Python 3.8+
- Bibliotecas Python:
  ```
  pydub
  SpeechRecognition
  ffmpeg-python
  ```
- **FFmpeg** instalado e configurado no sistema:
  - Adicione o caminho do executável `ffmpeg` ao PATH do sistema operacional.
  - Ou configure o caminho diretamente no script:
    ```python
    from pydub import AudioSegment
    AudioSegment.ffmpeg = r"caminho_para_ffmpeg/ffmpeg.exe"
    ```

---

## Instalação

1. **Clone ou Baixe o Repositório**:
   ```bash
   git clone https://github.com/seu-repositorio/transcritor-audio.git
   cd transcritor-audio
   ```

2. **Crie um Ambiente Virtual (Opcional):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate  # Windows
   ```

3. **Instale as Dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Certifique-se de que o FFmpeg está Instalado:**
   - [Instruções para instalação do FFmpeg](https://ffmpeg.org/download.html)

---

## Como Usar

1. Execute o script Python:
   ```bash
   python script.py
   ```

2. Na interface gráfica:
   - Clique em **Selecionar Arquivo de Áudio** e escolha o arquivo desejado.
   - Clique em **Iniciar Transcrição** para começar o processo.
   - Acompanhe o progresso na barra e nos detalhes exibidos.

3. Após a transcrição:
   - Escolha salvar o arquivo `.txt` em um local específico ou na pasta padrão `transcricoes`.

---

## Estrutura de Diretórios

Após executar o programa, a seguinte estrutura de diretórios será criada automaticamente:

```
projeto/
|-- script.py
|-- requirements.txt
|-- wav/               # Contém arquivos WAV convertidos
|-- transcricoes/      # Contém transcrições salvas em .txt
```

---

## Contribuição

1. Faça um fork do repositório.
2. Crie uma branch para sua feature ou correção de bug:
   ```bash
   git checkout -b minha-feature
   ```
3. Faça commit das suas alterações:
   ```bash
   git commit -m 'Adiciona nova feature'
   ```
4. Faça push para a branch:
   ```bash
   git push origin minha-feature
   ```
5. Abra um Pull Request.

---

## Licença

Este projeto está licenciado sob a [Licença MIT](LICENSE).

