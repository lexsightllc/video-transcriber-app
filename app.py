import streamlit as st
import os
import tempfile
import time
from pathlib import Path
from transcriber import transcribe_video, WHISPER_MODELS, SUPPORTED_LANGUAGES

# --- UI Configuration ---
st.set_page_config(
    page_title="Video Transcriber",
    page_icon="🎙️",
    layout="centered"
)

# --- Session State Initialization ---
if 'srt_content' not in st.session_state:
    st.session_state.srt_content = ""
if 'file_name' not in st.session_state:
    st.session_state.file_name = "transcription.srt"

# --- Header ---
st.title("🎙️ Aplicativo de Transcrição de Vídeos")
st.markdown("""
Este aplicativo utiliza o modelo Whisper para transcrever áudio de vídeos e gerar arquivos SRT (legendas).
""")

# --- Instructions Accordion ---
with st.expander("❓ Como usar?", expanded=False):
    st.markdown("""
    1.  **Faça upload do seu arquivo de vídeo** (MP4, MOV, MKV, etc.).
    2.  **Escolha o modelo Whisper** e o idioma do áudio.
    3.  Clique em "**Transcrever Vídeo**".
    4.  Aguarde a conclusão. O progresso será exibido.
    5.  O texto transcrito aparecerá abaixo, e você poderá baixar o arquivo SRT.
    """)
    st.info("A primeira transcrição pode demorar um pouco mais, pois o modelo Whisper será baixado.")

# --- File Uploader ---
uploaded_file = st.file_uploader(
    "1. Faça upload do seu arquivo de vídeo",
    type=["mp4", "mov", "avi", "mkv", "webm"],
    help="Formatos de vídeo suportados: MP4, MOV, AVI, MKV, WebM"
)

# --- Transcription Options ---
st.subheader("2. Opções de Transcrição")
col1, col2 = st.columns(2)

with col1:
    whisper_model = st.selectbox(
        "Selecione o modelo Whisper:",
        options=["base", "small", "medium", "large-v2"],
        index=0,  # Default to 'base'
        help="Modelos menores são mais rápidos, modelos maiores são mais precisos."
    )
with col2:
    audio_language = st.selectbox(
        "Selecione o idioma do áudio:",
        options=["pt", "en", "es", "fr", "de", "auto"],
        index=0,  # Default to 'pt'
        help="O idioma do áudio no vídeo. 'auto' tenta detectar o idioma."
    )

# --- Transcribe Button ---
if st.button("Transcrever Vídeo", type="primary", use_container_width=True):
    if uploaded_file is not None:
        st.session_state.srt_content = ""  # Clear previous content
        st.session_state.file_name = os.path.splitext(uploaded_file.name)[0] + ".srt"

        # Create a temporary file to save the uploaded video
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as temp_video_file:
            temp_video_file.write(uploaded_file.read())
            temp_video_path = temp_video_file.name

        try:
            # Use st.status for a nice progress indicator
            with st.status("Iniciando Transcrição...", expanded=True) as status_container:
                st.write(f"Preparando para transcrever `{uploaded_file.name}`...")
                
                # Define progress callback for transcriber
                def ui_progress_callback(step_description: str, percentage: float):
                    status_container.update(label=f"Transcrevendo: {step_description}", state="running", expanded=True)
                    st.progress(percentage / 100.0, text=f"{step_description} ({percentage:.1f}%)")
                    time.sleep(0.1)  # Small delay for UI to update properly

                srt_output = transcribe_video(
                    temp_video_path,
                    model_name=whisper_model,
                    language=audio_language if audio_language != "auto" else None,  # Pass None for auto-detection
                    progress_callback=ui_progress_callback
                )
                
                st.session_state.srt_content = srt_output
                status_container.update(label="Transcrição Concluída!", state="complete", expanded=False)
                st.success("Transcrição concluída com sucesso!")

        except FileNotFoundError:
            st.error("Erro: O arquivo de vídeo não foi encontrado. Por favor, tente novamente.")
        except ValueError as e:
            st.error(f"Erro de validação: {e}. Por favor, verifique o arquivo e tente novamente.")
        except Exception as e:
            st.error(f"Ocorreu um erro durante a transcrição: {e}")
            st.warning("Verifique se o arquivo é um vídeo válido e se contém áudio. Tente um modelo Whisper diferente.")
        finally:
            # Clean up the temporary video file
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)

    else:
        st.warning("Por favor, faça upload de um arquivo de vídeo primeiro.")

# --- Display Results ---
if st.session_state.srt_content:
    st.subheader("3. Transcrição Gerada")
    st.text_area(
        "Conteúdo SRT:",
        st.session_state.srt_content,
        height=300,
        help="Este é o conteúdo do arquivo SRT gerado."
    )

    st.download_button(
        label="Baixar Arquivo SRT",
        data=st.session_state.srt_content.encode("utf-8"),
        file_name=st.session_state.file_name,
        mime="application/x-subrip",
        use_container_width=True
    )
else:
    st.info("Faça upload de um vídeo e clique em 'Transcrever Vídeo' para ver os resultados aqui.")
