import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import speech_recognition as sr
import os
from pydub import AudioSegment
from datetime import datetime
import threading
import logging

# Caminho base e configuração do ffmpeg
caminho_da_pasta_base = os.path.join(os.path.dirname(__file__), "bin") 
AudioSegment.ffmpeg = os.path.join(caminho_da_pasta_base, "ffmpeg.exe")
AudioSegment.ffprobe = os.path.join(caminho_da_pasta_base, "ffprobe.exe")

# Configuração do logger
registrador_de_logs = logging.getLogger(__name__)
registrador_de_logs.setLevel(logging.DEBUG)

class ManipuladorDeTextoParaLog(logging.Handler):
    """Handler personalizado para direcionar logs para um widget de texto do Tkinter."""
    def __init__(self, widget_de_texto):
        super().__init__()
        self.widget_de_texto = widget_de_texto

    def emit(self, registro):
        mensagem = self.format(registro)
        self.widget_de_texto.after(0, self._adicionar_mensagem, mensagem)

    def _adicionar_mensagem(self, mensagem):
        self.widget_de_texto.configure(state='normal')
        self.widget_de_texto.insert(tk.END, mensagem + '\n')
        self.widget_de_texto.configure(state='disabled')
        self.widget_de_texto.yview(tk.END)

# Função para abrir a janela de seleção de arquivo de áudio
def selecionar_arquivo_de_audio(raiz):
    arquivo_de_audio = filedialog.askopenfilename(
        title="Selecione um arquivo de áudio",
        filetypes=[("Arquivos de Áudio", "*.mp3;*.wav;*.flac")],
    )
    if not arquivo_de_audio:
        raiz.quit()  # Fecha a aplicação caso o usuário cancele
    return arquivo_de_audio

# Função para abrir a janela de seleção da pasta de destino
def selecionar_pasta_de_destino(raiz):
    pasta_de_destino = filedialog.askdirectory(title="Selecione a pasta de destino")
    if not pasta_de_destino:
        raiz.quit()  # Fecha a aplicação caso o usuário cancele
    return pasta_de_destino

# Função para atualizar o progresso
def atualizar_progresso(barra_de_progresso, progresso, texto_de_status, texto):
    barra_de_progresso["value"] = progresso
    texto_de_status.config(text=texto)
    texto_de_status.update()

# Função para reiniciar a transcrição
def reiniciar_transcricao(janela_de_progresso, barra_de_progresso, texto_de_status, texto_do_log, raiz):
    # Limpar o conteúdo dos widgets
    texto_do_log.delete("1.0", tk.END)  # Usando texto_do_log aqui
    barra_de_progresso["value"] = 0
    texto_de_status.config(text="")

    # Reiniciar a transcrição
    caminho_do_audio = selecionar_arquivo_de_audio(raiz)
    if caminho_do_audio:
        iniciar_transcricao(caminho_do_audio, janela_de_progresso, barra_de_progresso, texto_de_status, texto_do_log, raiz)  # Passando todos os parâmetros
    else:
        registrador_de_logs.info("Nenhum arquivo foi selecionado. Encerrando o programa.")
        raiz.quit()  # Fecha a aplicação caso o usuário cancele a seleção

def converter_para_wav(caminho_do_audio, barra_de_progresso=None, texto_de_status=None):
    if caminho_do_audio.endswith(".mp3"):
        try:
            audio = AudioSegment.from_mp3(caminho_do_audio)
            caminho_do_audio_wav = caminho_do_audio.replace(".mp3", ".wav")
            audio.export(caminho_do_audio_wav, format="wav")

            if barra_de_progresso and texto_de_status:
                atualizar_progresso(barra_de_progresso, 50, texto_de_status, "Conversão de arquivo para WAV concluída")

            registrador_de_logs.info(f"Arquivo MP3 convertido para: {caminho_do_audio_wav}")
            return caminho_do_audio_wav
        except Exception as e:
            registrador_de_logs.error(f"Erro ao converter áudio para WAV: {e}")
            raise
    elif caminho_do_audio.endswith(".wav"):
        return caminho_do_audio
    else:
        registrador_de_logs.error("Formato de áudio não suportado. Por favor, forneça um arquivo .mp3 ou .wav.")
        raise ValueError("Formato de áudio não suportado.")

def converter_audio_para_texto_com_timestamps(caminho_do_audio, caminho_para_arquivo_de_texto_de_saida, janela_de_progresso, barra_de_progresso, texto_de_status, texto_do_log, raiz):
    reconhecedor_de_fala = sr.Recognizer()

    caminho_do_audio = converter_para_wav(caminho_do_audio, barra_de_progresso, texto_de_status)

    audio = AudioSegment.from_wav(caminho_do_audio)
    duracao_do_segmento_em_milisegundos = 60000  
    duracao_total_em_milisegundos = len(audio)
    numero_de_segmentos = duracao_total_em_milisegundos // duracao_do_segmento_em_milisegundos

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")  # Formato recomendado
    pasta_dos_segmentos = f"segmentos_{timestamp}"
    os.makedirs(pasta_dos_segmentos, exist_ok=True)

    texto_completo = ""
    atualizar_progresso(barra_de_progresso, 0, texto_de_status, "Iniciando transcrição...")

    for i in range(numero_de_segmentos + 1):
        inicio_em_milisegundos = i * duracao_do_segmento_em_milisegundos
        fim_em_milisegundos = min(inicio_em_milisegundos + duracao_do_segmento_em_milisegundos, duracao_total_em_milisegundos)
        segmento_do_audio = audio[inicio_em_milisegundos:fim_em_milisegundos]

        caminho_do_segmento_wav = os.path.join(pasta_dos_segmentos, f"segmento_{i}.wav")
        segmento_do_audio.export(caminho_do_segmento_wav, format="wav")

        with sr.AudioFile(caminho_do_segmento_wav) as fonte:
            dados_de_audio = reconhecedor_de_fala.record(fonte)

        try:
            texto_do_segmento = reconhecedor_de_fala.recognize_google(dados_de_audio, language='pt-BR')
            timestamp_inicio = f"{inicio_em_milisegundos // 60000:02}:{(inicio_em_milisegundos // 1000) % 60:02}"
            timestamp_fim = f"{fim_em_milisegundos // 60000:02}:{(fim_em_milisegundos // 1000) % 60:02}"
            texto_completo += f"[{timestamp_inicio} - {timestamp_fim}] {texto_do_segmento}\n\n"
            registrador_de_logs.info(f"Segmento {i + 1} transcrito com sucesso.")
        except sr.UnknownValueError:
            registrador_de_logs.warning(f"O Google Speech Recognition não conseguiu entender o áudio no segmento {i + 1}.")
        except sr.RequestError as erro:
            registrador_de_logs.error(f"Erro ao tentar se conectar ao Google Speech Recognition no segmento {i + 1}; {erro}")

        progresso = ((i + 1) / (numero_de_segmentos + 1)) * 100
        atualizar_progresso(barra_de_progresso, progresso, texto_de_status, f"Transcrevendo segmento {i + 1} de {numero_de_segmentos + 1}...")

        if(progresso == 100):
            atualizar_progresso(barra_de_progresso, progresso, texto_de_status, "Transcrição concluída.")

        os.remove(caminho_do_segmento_wav)

    # Usando o método `after()` para chamar a janela de diálogo na thread principal
    def salvar_arquivo():
        caminho_para_arquivo_de_texto_de_saida = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Arquivos de Texto", "*.txt")],
            title="Salvar Transcrição",
            initialfile=f"transcricao_{timestamp}.txt"
        )

        if caminho_para_arquivo_de_texto_de_saida:
            with open(caminho_para_arquivo_de_texto_de_saida, "w", encoding="utf-8") as arquivo:
                arquivo.write(texto_completo)
            registrador_de_logs.info(f"Transcrição salva em: {caminho_para_arquivo_de_texto_de_saida}")
        else:
            registrador_de_logs.warning("Nenhum local foi selecionado para salvar o arquivo de transcrição.")

        os.rmdir(pasta_dos_segmentos)
        janela_de_progresso.update_idletasks()

    # Agendar a função salvar_arquivo para ser chamada na thread principal
    janela_de_progresso.after(0, salvar_arquivo)


# Função para iniciar a transcrição em uma thread separada
def iniciar_transcricao(caminho_do_audio, janela_de_progresso=None, barra_de_progresso=None, texto_de_status=None, texto_do_log=None, raiz=None):
    if janela_de_progresso:
        # Limpar o log existente e resetar a barra de progresso
        if texto_do_log:
            texto_do_log.delete("1.0", tk.END)
        if barra_de_progresso:
            barra_de_progresso["value"] = 0
    else:
        # Criação da janela de progresso se for a primeira vez
        janela_de_progresso = tk.Tk()
        janela_de_progresso.title("Progresso da Transcrição")
        botao_nova_transcricao = tk.Button(janela_de_progresso, text="Iniciar nova transcrição", 
                                            command=lambda: reiniciar_transcricao(janela_de_progresso, barra_de_progresso, texto_de_status, texto_do_log, raiz))  # Passando os parâmetros necessários
        botao_nova_transcricao.pack(pady=10)

        barra_de_progresso = ttk.Progressbar(janela_de_progresso, length=300, mode="determinate", maximum=100)
        barra_de_progresso.pack(pady=10)

        texto_de_status = tk.Label(janela_de_progresso, text="")
        texto_de_status.pack(pady=10)

        quadro_do_log = tk.Frame(janela_de_progresso)
        quadro_do_log.pack(pady=10)

        etiqueta_do_log = tk.Label(quadro_do_log, text="Log de Progresso:")
        etiqueta_do_log.pack(anchor="w")

        texto_do_log = tk.Text(quadro_do_log, height=10, width=50)
        texto_do_log.pack()

        # Configuração do Handler para exibir logs sem data e hora
        manipulador_de_log = ManipuladorDeTextoParaLog(texto_do_log)
        manipulador_de_log.setFormatter(logging.Formatter('%(message)s'))  # Exibe apenas a mensagem, sem data e hora
        registrador_de_logs.addHandler(manipulador_de_log)

        iniciar_transcricao.janela_de_progresso = janela_de_progresso  # Armazena a janela para reutilização

    thread_de_transcricao = threading.Thread(
        target=converter_audio_para_texto_com_timestamps,
        args=(caminho_do_audio, None, janela_de_progresso, barra_de_progresso, texto_de_status, texto_do_log, raiz)  # Passando todos os parâmetros
    )
    thread_de_transcricao.daemon = True  # Define a thread como daemon
    thread_de_transcricao.start()

    # Manipulador do evento de fechamento da janela principal
    def fechar_programa():
        if thread_de_transcricao.is_alive():
            registrador_de_logs.info("A transcrição foi interrompida.")
        raiz.quit()
        raiz.destroy()
        janela_de_progresso.quit()
        janela_de_progresso.destroy()

    raiz.protocol("WM_DELETE_WINDOW", fechar_programa)

    janela_de_progresso.mainloop()

# Seleção de arquivo e início do processo
raiz = tk.Tk()
raiz.withdraw()  # Mantém a janela principal oculta

caminho_do_audio = selecionar_arquivo_de_audio(raiz)

if caminho_do_audio:
    iniciar_transcricao(caminho_do_audio, raiz=raiz)
else:
    registrador_de_logs.info("Nenhum arquivo foi selecionado. Encerrando o programa.")
    raiz.quit()  # Garante que o programa será fechado
