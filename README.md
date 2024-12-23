# Conversor de Áudio para Texto com Timestamps

Este projeto é um aplicativo Python com interface gráfica (GUI) baseado em Tkinter para converter arquivos de áudio (MP3 e WAV) em texto, incluindo timestamps, utilizando o Google Speech Recognition.

## Funcionalidades

- Suporte a arquivos MP3 e WAV.
- Conversão de áudio para texto com marcação de tempo (timestamps).
- Exibição do progresso da transcrição em uma barra de progresso.
- Log em tempo real exibido na interface gráfica.
- Salvamento do texto transcrito em um arquivo .txt.

---

## Requisitos

Certifique-se de ter os seguintes itens instalados:

- Python 3.10 ou superior
- Pip (gerenciador de pacotes do Python)

### Bibliotecas Necessárias

As bibliotecas usadas no projeto podem ser instaladas via `pip`. Execute o seguinte comando para instalar todas as dependências:

```bash
pip install -r requirements.txt
```

Conteúdo do arquivo `requirements.txt`:
```plaintext
speechrecognition
ffmpeg-python
tk
```

---

## Instalação e Configuração

1. **Clone o repositório**:

   ```bash
   git clone <URL_DO_REPOSITORIO>
   cd <PASTA_DO_PROJETO>
   ```

2. **Instale os pacotes necessários**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Certifique-se de que o FFmpeg está instalado no sistema**:
   
   - Baixe o FFmpeg [aqui](https://ffmpeg.org/download.html).
   - Siga as instruções para adicionar o executável do FFmpeg ao PATH do sistema.
   
   Para verificar se o FFmpeg está corretamente configurado, execute:
   ```bash
   ffmpeg -version
   ```

---

## Como Usar

1. **Execute o script**:

   ```bash
   python script.py
   ```

2. **Selecione um arquivo de áudio**:
   - Uma janela será exibida para você escolher um arquivo MP3 ou WAV.

3. **Acompanhe o progresso**:
   - O progresso da transcrição será exibido em uma nova janela com uma barra de progresso e logs em tempo real.

4. **Aguarde a finalização**:
   - Ao término, o texto transcrito será salvo em um arquivo `.txt` na mesma pasta do script, com o nome baseado na data e hora atuais.

---

## Estrutura do Código

- **GUI com Tkinter**: Interface gráfica para seleção de arquivos e exibição do progresso.
- **Threading**: Transcrição executada em segundo plano para manter a interface responsiva.
- **Logs**: Log personalizado exibido na interface.
- **Conversão de Áudio**: Utiliza `ffmpeg-python` para converter MP3 em WAV, caso necessário.
- **Reconhecimento de Voz**: Utiliza `SpeechRecognition` com o Google Speech API.

---

## Possíveis Erros e Soluções

1. **Erro: `ffmpeg not found`**:
   - Certifique-se de que o FFmpeg está instalado e configurado no PATH do sistema.

2. **Erro: `Google Speech Recognition não conseguiu entender o áudio`**:
   - O áudio pode estar em má qualidade ou conter ruídos excessivos. Tente um arquivo com melhor qualidade.

3. **Erro: `Connection error with Google Speech API`**:
   - Verifique sua conexão com a internet.

---

## Contribuições

Sinta-se à vontade para abrir issues ou pull requests caso encontre bugs ou tenha sugestões de melhorias.
