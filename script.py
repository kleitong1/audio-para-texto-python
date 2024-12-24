import os
import sys
import ctypes
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from pydub import AudioSegment
import speech_recognition as sr
import tempfile
import threading
from datetime import datetime
import time

class TranscritorDeAudio:
    def __init__(self, raiz):
        self.raiz = raiz
        self.raiz.title("Transcrição de Áudio")
        self.raiz.geometry("500x400")

        # Configurações iniciais
        self.arquivo_audio = None
        self.progresso = tk.IntVar()

        # Layout
        self.criar_componentes()

    def criar_componentes(self):
        ttk.Label(self.raiz, text="Bem-vindo ao Transcritor de Áudio", font=("Arial", 14)).pack(pady=10)

        self.botao_selecionar = ttk.Button(self.raiz, text="Selecionar Arquivo de Áudio", command=self.selecionar_audio)
        self.botao_selecionar.pack(pady=5)

        self.botao_iniciar = ttk.Button(self.raiz, text="Iniciar Transcrição", command=self.iniciar_transcricao, state="disabled")
        self.botao_iniciar.pack(pady=5)

        self.barra_progresso = ttk.Progressbar(self.raiz, orient="horizontal", length=400, mode="determinate", variable=self.progresso)
        self.barra_progresso.pack(pady=10)

        self.rotulo_status = ttk.Label(self.raiz, text="Status: Aguardando arquivo.")
        self.rotulo_status.pack(pady=10)

        self.texto_detalhes = tk.Text(self.raiz, wrap="word", height=10, width=60, state="disabled")
        self.texto_detalhes.pack(pady=5)

    def registrar_detalhes(self, mensagem):
        """Atualiza a área de detalhes na interface com novas mensagens."""
        self.texto_detalhes.configure(state="normal")
        self.texto_detalhes.insert(tk.END, mensagem + "\n")
        self.texto_detalhes.see(tk.END)  # Rola para o final
        self.texto_detalhes.configure(state="disabled")

    def selecionar_audio(self):
        self.arquivo_audio = filedialog.askopenfilename(
            title="Selecione um arquivo de áudio",
            filetypes=[("Arquivos de Áudio", "*.mp3;*.wav;*.flac")]
        )

        if self.arquivo_audio:
            self.rotulo_status.config(text=f"Arquivo selecionado: {os.path.basename(self.arquivo_audio)}")
            self.botao_iniciar.config(state="normal")
        else:
            self.rotulo_status.config(text="Nenhum arquivo selecionado.")

    def iniciar_transcricao(self):
        if not self.arquivo_audio:
            messagebox.showerror("Erro", "Nenhum arquivo selecionado.")
            return

        self.botao_iniciar.config(state="disabled")
        self.rotulo_status.config(text="Iniciando transcrição...")
        self.registrar_detalhes("Iniciando transcrição do arquivo...")
        threading.Thread(target=self.transcrever_audio).start()

    def transcrever_audio(self):
        try:
            inicio = time.time()
            self.progresso.set(0)
            arquivo_wav = self.converter_para_wav(self.arquivo_audio)
            self.registrar_detalhes(f"Arquivo WAV gerado: {arquivo_wav}")
            transcricao = self.converter_audio_para_texto(arquivo_wav)
            self.salvar_transcricao(transcricao)
            tempo_decorrido = time.time() - inicio
            self.rotulo_status.config(text="Transcrição concluída!")
            self.registrar_detalhes(f"Transcrição concluída em {tempo_decorrido:.2f} segundos.")
        except Exception as e:
            self.registrar_detalhes(f"Erro durante a transcrição: {e}")
            self.rotulo_status.config(text="Erro durante a transcrição.")
            messagebox.showerror("Erro", f"Falha na transcrição: {e}")
        finally:
            self.botao_iniciar.config(state="normal")

    def converter_para_wav(self, arquivo_audio):
        self.registrar_detalhes("Convertendo o arquivo para WAV...")
        try:
            pasta_wav = os.path.join(os.getcwd(), "wav")
            if not os.path.exists(pasta_wav):
                os.makedirs(pasta_wav)

            caminho_saida_wav = os.path.join(pasta_wav, f"{os.path.splitext(os.path.basename(arquivo_audio))[0]}.wav")
            if arquivo_audio.lower().endswith(".mp3"):
                audio = AudioSegment.from_mp3(arquivo_audio)
                audio.export(caminho_saida_wav, format="wav")
                self.registrar_detalhes("Conversão concluída para WAV.")
                return caminho_saida_wav
            elif arquivo_audio.lower().endswith(".wav"):
                self.registrar_detalhes("O arquivo já está em formato WAV.")
                return arquivo_audio
            else:
                raise ValueError("Formato de áudio não suportado. Use .mp3 ou .wav.")
        except Exception as e:
            self.registrar_detalhes(f"Erro ao converter para WAV: {e}")
            raise

    def converter_audio_para_texto(self, arquivo_audio):
        self.registrar_detalhes("Iniciando divisão do áudio em segmentos fixos...")
        reconhecedor = sr.Recognizer()
        audio = AudioSegment.from_wav(arquivo_audio)

        duracao_segmento = 60000  # 1 minuto em milissegundos
        duracao_total = len(audio)
        transcricao = []

        for inicio in range(0, duracao_total, duracao_segmento):
            fim = min(inicio + duracao_segmento, duracao_total)
            segmento = audio[inicio:fim]

            self.registrar_detalhes(f"Processando segmento de {inicio // 1000}s a {fim // 1000}s...")
            caminho_segmento = os.path.join(os.getcwd(), f"segmento_{inicio // 1000}_{fim // 1000}.wav")
            
            try:
                segmento.export(caminho_segmento, format="wav")
                self.registrar_detalhes(f"Segmento exportado para {caminho_segmento}")

                with sr.AudioFile(caminho_segmento) as fonte:
                    dados = reconhecedor.record(fonte)
                    texto = reconhecedor.recognize_google(dados, language="pt-BR")
                    transcricao.append(f"[{inicio // 1000}s - {fim // 1000}s]:\n{texto}\n")
                    self.registrar_detalhes(f"Segmento de {inicio // 1000}s a {fim // 1000}s transcrito com sucesso.")
            except sr.UnknownValueError:
                transcricao.append(f"[{inicio // 1000}s - {fim // 1000}s]:\n[INAUDÍVEL]\n")
                self.registrar_detalhes(f"Segmento de {inicio // 1000}s a {fim // 1000}s marcado como inaudível.")
            except sr.RequestError as e:
                self.registrar_detalhes(f"Erro na API de transcrição: {e}")
                raise
            except Exception as e:
                self.registrar_detalhes(f"Erro inesperado no segmento: {e}")
                raise
            finally:
                if os.path.exists(caminho_segmento):
                    os.unlink(caminho_segmento)  # Remove o arquivo temporário

            # Atualiza a barra de progresso
            progresso_percentual = int(((fim) / duracao_total) * 100)
            self.progresso.set(progresso_percentual)

        return "".join(transcricao)

    def salvar_transcricao(self, transcricao):
        self.registrar_detalhes("Salvando transcrição...")

        # Perguntar ao usuário se deseja escolher o diretório
        if messagebox.askyesno("Salvar Arquivo", "Deseja escolher o local para salvar o arquivo?"):
            caminho_salvar = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Arquivos de Texto", "*.txt")],
                title="Salvar Transcrição",
                initialfile=f"transcricao_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.txt"
            )
        else:
            pasta_transcricoes = os.path.join(os.getcwd(), "transcricoes")
            if not os.path.exists(pasta_transcricoes):
                os.makedirs(pasta_transcricoes)
            caminho_salvar = os.path.join(pasta_transcricoes, f"transcricao_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.txt")

        if caminho_salvar:
            with open(caminho_salvar, "w", encoding="utf-8") as arquivo:
                arquivo.write(transcricao)
            messagebox.showinfo("Sucesso", f"Transcrição salva em: {caminho_salvar}")
            self.registrar_detalhes(f"Transcrição salva em: {caminho_salvar}")
        else:
            messagebox.showinfo("Cancelado", "A transcrição não foi salva.")
            self.registrar_detalhes("O usuário cancelou o salvamento da transcrição.")

if __name__ == "__main__":
    if os.name == "nt":
        ctypes.windll.kernel32.FreeConsole()  # Oculta o terminal

    if os.name == "nt" and not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    else:
        raiz = tk.Tk()
        app = TranscritorDeAudio(raiz)
        raiz.mainloop()
