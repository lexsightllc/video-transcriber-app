"""Streamlit application for enhanced video transcription."""

from __future__ import annotations

import json
import tempfile
import time
from pathlib import Path

import streamlit as st

from ..phi3_brain import Phi3Brain
from ..transcriber import (
    SUPPORTED_LANGUAGES,
    WHISPER_MODELS,
    transcribe_video,
    transcribe_video_enhanced,
)

# --- UI Configuration ---
st.set_page_config(
    page_title="🧠 Enhanced Video Transcriber with Phi-3 Brain",
    page_icon="🧠",
    layout="wide"
)

# --- Session State Initialization ---
if 'transcription_result' not in st.session_state:
    st.session_state.transcription_result = None
if 'phi3_brain' not in st.session_state:
    st.session_state.phi3_brain = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# --- Header ---
st.title("🧠 Enhanced Video Transcriber with Phi-3 Brain")
st.markdown("""
🎯 **Next-generation video transcription** powered by Whisper + Phi-3 AI Brain  
📊 Get intelligent analysis, summaries, and insights beyond basic transcription
""")

# --- Instructions Accordion ---
with st.expander("❓ How to use the Enhanced Transcriber", expanded=False):
    st.markdown("""
    **🎬 Basic Transcription:**
    1. Upload your video file (MP4, MOV, MKV, etc.)
    2. Choose Whisper model and audio language
    3. Click "**Transcribe Video**"
    
    **🧠 Phi-3 Brain Features:**
    - **Smart Analysis**: Quality assessment, sentiment analysis
    - **Intelligent Summaries**: Key topics and insights
    - **Interactive Q&A**: Ask questions about your video content
    - **Enhanced Metadata**: Comprehensive content analysis
    
    **💡 Pro Tips:**
    - Enable Phi-3 Brain for advanced analysis
    - Use Interactive Q&A to explore your content
    - Download JSON analysis for detailed insights
    """)
    st.info("🚀 First run may take longer as models are downloaded. Phi-3 requires significant computational resources.")

# --- Main Interface ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📁 Upload & Configure")
    
    # File Upload
    uploaded_file = st.file_uploader(
        "Upload your video file",
        type=["mp4", "mov", "avi", "mkv", "webm"],
        help="Supported formats: MP4, MOV, AVI, MKV, WebM"
    )
    
    # Transcription Options
    st.subheader("⚙️ Transcription Settings")
    
    col1_1, col1_2 = st.columns(2)
    with col1_1:
        whisper_model = st.selectbox(
            "Whisper Model",
            WHISPER_MODELS,
            index=1,  # Default to 'base'
            help="Larger models are more accurate but slower"
        )
    
    with col1_2:
        audio_language = st.selectbox(
            "Audio Language",
            ["auto"] + SUPPORTED_LANGUAGES,
            help="Select 'auto' for automatic detection"
        )
    
    # Phi-3 Brain Options
    st.subheader("🧠 Phi-3 Brain Settings")
    enable_phi3 = st.checkbox("Enable Phi-3 Brain Analysis", value=True, help="Advanced AI analysis and insights")
    
    if enable_phi3:
        analysis_options = st.multiselect(
            "Analysis Features",
            ["Quality Assessment", "Sentiment Analysis", "Key Topics", "Summary", "Q&A Generation"],
            default=["Quality Assessment", "Summary", "Key Topics"],
            help="Select which analysis features to enable"
        )
    
    # Process Button
    process_button = st.button(
        "🚀 Transcribe & Analyze Video",
        disabled=uploaded_file is None,
        use_container_width=True
    )

with col2:
    st.subheader("📊 Results & Analysis")
    
    if process_button and uploaded_file:
        # Create progress containers
        progress_container = st.container()
        result_container = st.container()
        
        with progress_container:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def ui_progress_callback(step_description: str, percentage: float):
                progress_bar.progress(percentage / 100)
                status_text.text(f"{step_description} ({percentage:.1f}%)")
        
        temp_video_path: Path | None = None

        try:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=Path(uploaded_file.name).suffix
            ) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_video_path = Path(tmp_file.name)

            if temp_video_path is None:
                raise RuntimeError("Temporary video file could not be created.")

            # Process video
            if enable_phi3:
                result = transcribe_video_enhanced(
                    str(temp_video_path),
                    model_name=whisper_model,
                    language=audio_language if audio_language != "auto" else "pt",
                    enable_phi3=True,
                    progress_callback=ui_progress_callback
                )
                st.session_state.transcription_result = result
            else:
                srt_content = transcribe_video(
                    str(temp_video_path),
                    model_name=whisper_model,
                    language=audio_language if audio_language != "auto" else "pt",
                    progress_callback=ui_progress_callback
                )
                st.session_state.transcription_result = {
                    "transcription": srt_content,
                    "phi3_enabled": False
                }
            
            # Clean up
            if temp_video_path is not None:
                temp_video_path.unlink(missing_ok=True)

            # Clear progress
            progress_container.empty()

        except Exception as exc:
            st.error(f"❌ Error processing video: {exc}")
            if temp_video_path is not None:
                temp_video_path.unlink(missing_ok=True)

# --- Results Display ---
if st.session_state.transcription_result:
    result = st.session_state.transcription_result
    
    st.markdown("---")
    st.subheader("📄 Transcription Results")
    
    # Tabs for different views
    if result.get("phi3_enabled", False) and "phi3_analysis" in result:
        tab1, tab2, tab3, tab4 = st.tabs(["📝 Transcription", "🧠 AI Analysis", "💬 Interactive Q&A", "📊 Raw Data"])
    else:
        tab1, tab4 = st.tabs(["📝 Transcription", "📊 Raw Data"])
    
    with tab1:
        st.text_area(
            "SRT Content",
            value=result["transcription"],
            height=400,
            help="Copy this content or download as SRT file"
        )
        
        # Download buttons
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            st.download_button(
                "📥 Download SRT",
                data=result["transcription"],
                file_name=f"{uploaded_file.name if uploaded_file else 'transcription'}.srt",
                mime="text/plain"
            )
        
        if result.get("phi3_enabled", False):
            with col_d2:
                st.download_button(
                    "📥 Download JSON Analysis",
                    data=json.dumps(result, indent=2, ensure_ascii=False),
                    file_name=f"{uploaded_file.name if uploaded_file else 'analysis'}.json",
                    mime="application/json"
                )
    
    # Phi-3 Analysis Tab
    if result.get("phi3_enabled", False) and "phi3_analysis" in result:
        analysis = result["phi3_analysis"]
        
        with tab2:
            if "error" in analysis:
                st.error(f"❌ Analysis failed: {analysis['error']}")
            else:
                # Summary
                if "summary" in analysis:
                    st.subheader("📋 Summary")
                    st.write(analysis["summary"])
                
                # Key Topics
                if "key_topics" in analysis and analysis["key_topics"]:
                    st.subheader("🏷️ Key Topics")
                    for topic in analysis["key_topics"]:
                        st.badge(topic)
                
                # Quality Assessment
                if "quality_assessment" in analysis:
                    qa = analysis["quality_assessment"]
                    st.subheader("⭐ Quality Assessment")
                    
                    col_qa1, col_qa2 = st.columns(2)
                    with col_qa1:
                        if "quality_score" in qa:
                            st.metric("Quality Score", f"{qa['quality_score']}/10")
                    with col_qa2:
                        if "confidence_level" in qa:
                            st.metric("Confidence", qa["confidence_level"])
                
                # Sentiment Analysis
                if "sentiment_analysis" in analysis:
                    sa = analysis["sentiment_analysis"]
                    st.subheader("😊 Sentiment Analysis")
                    
                    col_sa1, col_sa2 = st.columns(2)
                    with col_sa1:
                        if "sentiment" in sa:
                            st.metric("Overall Sentiment", sa["sentiment"])
                    with col_sa2:
                        if "tone" in sa:
                            st.metric("Tone", sa["tone"])
                
                # Statistics
                if "word_count" in analysis:
                    st.subheader("📊 Statistics")
                    col_st1, col_st2 = st.columns(2)
                    with col_st1:
                        st.metric("Word Count", analysis["word_count"])
                    with col_st2:
                        if "estimated_duration_minutes" in analysis:
                            st.metric("Est. Duration", f"{analysis['estimated_duration_minutes']:.1f} min")
        
        # Interactive Q&A Tab
        with tab3:
            st.subheader("💬 Ask Questions About Your Video")
            
            # Initialize Phi-3 brain if needed
            if st.session_state.phi3_brain is None:
                with st.spinner("🧠 Initializing Phi-3 Brain..."):
                    try:
                        st.session_state.phi3_brain = Phi3Brain()
                        st.success("✅ Phi-3 Brain ready!")
                    except Exception as e:
                        st.error(f"❌ Failed to initialize Phi-3 Brain: {e}")
                        st.session_state.phi3_brain = None
            
            if st.session_state.phi3_brain:
                # Suggested questions
                if "suggested_questions" in analysis and analysis["suggested_questions"]:
                    st.subheader("💡 Suggested Questions")
                    for i, question in enumerate(analysis["suggested_questions"]):
                        if st.button(f"❓ {question}", key=f"suggested_{i}"):
                            st.session_state.chat_history.append({"type": "question", "content": question})
                            with st.spinner("🧠 Thinking..."):
                                answer = st.session_state.phi3_brain.answer_question(result["transcription"], question)
                                st.session_state.chat_history.append({"type": "answer", "content": answer})
                            st.rerun()
                
                # Chat interface
                st.subheader("💭 Custom Questions")
                user_question = st.text_input("Ask a question about the video content:", key="user_question")
                
                if st.button("Ask Question") and user_question:
                    st.session_state.chat_history.append({"type": "question", "content": user_question})
                    with st.spinner("🧠 Thinking..."):
                        answer = st.session_state.phi3_brain.answer_question(result["transcription"], user_question)
                        st.session_state.chat_history.append({"type": "answer", "content": answer})
                    st.rerun()
                
                # Display chat history
                if st.session_state.chat_history:
                    st.subheader("💬 Q&A History")
                    for i, item in enumerate(st.session_state.chat_history):
                        if item["type"] == "question":
                            st.write(f"❓ **Q{i//2 + 1}:** {item['content']}")
                        else:
                            st.write(f"💡 **A{i//2 + 1}:** {item['content']}")
                            st.markdown("---")
                
                # Clear chat button
                if st.session_state.chat_history:
                    if st.button("🗑️ Clear Chat History"):
                        st.session_state.chat_history = []
                        st.rerun()
    
    # Raw Data Tab
    with tab4:
        st.subheader("📊 Raw Analysis Data")
        st.json(result)

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    🧠 Enhanced Video Transcriber powered by Whisper + Phi-3 Brain<br>
    Built with Streamlit • Advanced AI Analysis • Interactive Q&A
</div>
""", unsafe_allow_html=True)
