import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import speech_recognition as sr
import os
from pydub import AudioSegment
from datetime import datetime
import threading
import logging

# Configuração do logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class TextHandler(logging.Handler):
    """Handler personalizado para direcionar logs para um widget de texto do Tkinter."""
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.after(0, self._append, msg)

    def _append(self, msg):
        self.text_widget.configure(state='normal')
        self.text_widget.insert(tk.END, msg + '\n')
        self.text_widget.configure(state='disabled')
        self.text_widget.yview(tk.END)

# Função para abrir a modal de seleção de arquivo de áudio
def selecionar_arquivo_audio():
    root = tk.Tk()
    root.withdraw()
    arquivo_audio = filedialog.askopenfilename(
        title="Selecione um arquivo de áudio",
        filetypes=[("Arquivos de Áudio", "*.mp3;*.wav;*.flac")],
    )
    return arquivo_audio if arquivo_audio else None

# Função para atualizar o progresso
def atualizar_progresso(progress_bar, progresso, texto_status, texto):
    progress_bar["value"] = progresso
    texto_status.config(text=texto)
    texto_status.update()

# Função para adicionar mensagens ao painel de log
def adicionar_log(text_widget, mensagem):
    texto_atual = text_widget.get("1.0", tk.END)
    texto_atual += mensagem + "\n"
    text_widget.delete("1.0", tk.END)
    text_widget.insert(tk.END, texto_atual)
    text_widget.yview(tk.END)

# Função para converter áudio em texto com timestamps
def converter_audio_para_texto_com_timestamps(audio_path, texto_output_path, progress_window, progress_bar, texto_status, text_widget):
    recognizer = sr.Recognizer()

    if audio_path.endswith(".mp3"):
        audio = AudioSegment.from_mp3(audio_path)
        audio_wav_path = audio_path.replace(".mp3", ".wav")
        audio.export(audio_wav_path, format="wav")
        audio_path = audio_wav_path
        logger.info(f"Arquivo MP3 convertido para: {audio_wav_path}")
    elif not audio_path.endswith(".wav"):
        logger.error("Formato de áudio não suportado. Por favor, forneça um arquivo .mp3 ou .wav.")
        return

    audio = AudioSegment.from_wav(audio_path)
    segment_duration_ms = 30000  # 30 segundos
    total_duration_ms = len(audio)
    num_segments = total_duration_ms // segment_duration_ms

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    pasta_segmentos = f"segmentos_{timestamp}"
    os.makedirs(pasta_segmentos, exist_ok=True)

    texto_completo = ""

    for i in range(num_segments + 1):
        start_ms = i * segment_duration_ms
        end_ms = min(start_ms + segment_duration_ms, total_duration_ms)
        audio_segment = audio[start_ms:end_ms]

        segment_wav_path = os.path.join(pasta_segmentos, f"segmento_{i}.wav")
        audio_segment.export(segment_wav_path, format="wav")

        with sr.AudioFile(segment_wav_path) as source:
            audio_data = recognizer.record(source)

        try:
            texto_segmento = recognizer.recognize_google(audio_data, language='pt-BR')
            timestamp_inicio = f"{start_ms // 60000:02}:{(start_ms // 1000) % 60:02}"
            timestamp_fim = f"{end_ms // 60000:02}:{(end_ms // 1000) % 60:02}"
            texto_completo += f"[{timestamp_inicio} - {timestamp_fim}] {texto_segmento}\n\n"
            logger.info(f"Segmento {i + 1} transcrito com sucesso.")
        except sr.UnknownValueError:
            logger.warning(f"O Google Speech Recognition não conseguiu entender o áudio no segmento {i + 1}.")
        except sr.RequestError as e:
            logger.error(f"Erro ao tentar se conectar ao Google Speech Recognition no segmento {i + 1}; {e}")

        progresso = ((i + 1) / (num_segments + 1)) * 100
        atualizar_progresso(progress_bar, progresso, texto_status, f"Transcrevendo segmento {i + 1} de {num_segments + 1}...")

        os.remove(segment_wav_path)

    texto_output_path = f"transcricao_{timestamp}.txt" if texto_output_path is None else texto_output_path

    with open(texto_output_path, "w", encoding="utf-8") as arquivo:
        arquivo.write(texto_completo)
    logger.info(f"Transcrição salva em: {texto_output_path}")

    os.rmdir(pasta_segmentos)

    # Finalizar o processo
    progress_window.quit()
    progress_window.destroy()

# Função para iniciar a transcrição em uma thread separada
def iniciar_transcricao(audio_path):
    progress_window = tk.Tk()
    progress_window.title("Progresso da Transcrição")

    status_label = tk.Label(progress_window, text="Transcrevendo áudio...")
    status_label.pack(pady=10)

    progress_bar = ttk.Progressbar(progress_window, length=300, mode="determinate", maximum=100)
    progress_bar.pack(pady=10)

    texto_status = tk.Label(progress_window, text="")
    texto_status.pack(pady=10)

    log_frame = tk.Frame(progress_window)
    log_frame.pack(pady=10)

    log_label = tk.Label(log_frame, text="Log de Progresso:")
    log_label.pack(anchor="w")

    log_text = tk.Text(log_frame, height=10, width=50)
    log_text.pack()

    # Configuração do Handler para exibir logs sem data e hora
    log_handler = TextHandler(log_text)
    log_handler.setFormatter(logging.Formatter('%(message)s'))  # Exibe apenas a mensagem, sem data e hora
    logger.addHandler(log_handler)

    transcricao_thread = threading.Thread(
        target=converter_audio_para_texto_com_timestamps,
        args=(audio_path, None, progress_window, progress_bar, texto_status, log_text)
    )
    transcricao_thread.daemon = True  # Define a thread como daemon
    transcricao_thread.start()

    progress_window.mainloop()

audio_path = selecionar_arquivo_audio()

if audio_path:
    iniciar_transcricao(audio_path)
else:
    logger.info("Nenhum arquivo foi selecionado. Encerrando o programa.")
