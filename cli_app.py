#!/usr/bin/env python3
"""
Enhanced Command-line interface for video transcription with Phi-3 brain integration.
This script provides an intelligent CLI wrapper with advanced analysis capabilities.
"""

import argparse
import os
import sys
import json
from transcriber import transcribe_video, transcribe_video_enhanced, logger
from phi3_brain import Phi3Brain

# --- INSTRUÇÕES DE INSTALAÇÃO ---
# Antes de executar este script, certifique-se de ter as bibliotecas necessárias instaladas.
# É ALTAMENTE RECOMENDADO usar um ambiente virtual (venv) para isolar as dependências.
#
# Abra seu terminal ou prompt de comando e execute os seguintes comandos:
#
# 1. Crie e ative um ambiente virtual (opcional, mas recomendado):
#    python -m venv venv_transcribe
#    # No Windows:
#    .\venv_transcribe\Scripts\activate
#    # No macOS/Linux:
#    source venv_transcribe/bin/activate
#
# 2. Instalar as dependências do requirements.txt:
#    Crie um arquivo 'requirements.txt' com o seguinte conteúdo:
#    moviepy>=1.0.3
#    openai-whisper>=20230314
#    # Se você tiver problemas com PyTorch no Windows/Linux sem GPU, adicione uma linha para PyTorch CPU:
#    # torch>=2.0.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
#    # Então instale com:
#    pip install -r requirements.txt
#
# 3. moviepy pode precisar do FFmpeg. Na maioria dos sistemas, moviepy tenta encontrá-lo
#    automaticamente. Se você tiver problemas, pode precisar instalar o FFmpeg separadamente:
#    - No Windows: Baixe de ffmpeg.org e adicione ao PATH do sistema.
#    - No macOS: brew install ffmpeg (com Homebrew)
#    - No Linux: sudo apt update && sudo apt install ffmpeg (para Debian/Ubuntu)
#
# 4. Para usuários de Windows/Linux que usam apenas CPU e estão tendo problemas com PyTorch e Whisper:
#    Pode ser necessário instalar PyTorch explicitamente para CPU antes do whisper (ou reinstalar):
#    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
#    Se já instalou whisper, desinstale e reinstale com:
#    pip install --upgrade --no-deps openai-whisper
#    pip install --upgrade --force-reinstall --no-deps torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
# ---------------------------------


def cli_progress_callback(step_description: str, percentage: float):
    """Callback function for CLI progress updates."""
    sys.stdout.write(f"\rProgresso: {step_description} ({percentage:.1f}%)")
    sys.stdout.flush()


def main():
    """Enhanced main CLI function with Phi-3 brain integration."""
    parser = argparse.ArgumentParser(
        description="🧠 Enhanced Video Transcription with Phi-3 Brain - Intelligent analysis beyond basic transcription",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic transcription with Phi-3 analysis
  python cli_app.py video.mp4
  
  # Advanced transcription with specific model
  python cli_app.py video.mp4 --model medium --lang en --phi3
  
  # Interactive Q&A mode
  python cli_app.py video.mp4 --interactive
  
  # Analysis only (requires existing transcription)
  python cli_app.py --analyze-only transcription.txt
        """
    )
    
    parser.add_argument(
        "input_file", 
        type=str, 
        nargs='?',
        help="Path to video file or transcription text file (for analysis-only mode)"
    )
    parser.add_argument(
        "--model", 
        type=str, 
        default="base", 
        choices=["tiny", "base", "small", "medium", "large", "large-v2"],
        help="Whisper model to use"
    )
    parser.add_argument(
        "--lang", 
        type=str, 
        default="pt", 
        help="Audio language (e.g., 'pt', 'en')"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        help="Output path for SRT file"
    )
    parser.add_argument(
        "--phi3", 
        action="store_true", 
        default=True,
        help="Enable Phi-3 brain analysis (default: enabled)"
    )
    parser.add_argument(
        "--no-phi3", 
        action="store_true", 
        help="Disable Phi-3 brain analysis"
    )
    parser.add_argument(
        "--interactive", 
        action="store_true", 
        help="Enable interactive Q&A mode after transcription"
    )
    parser.add_argument(
        "--analyze-only", 
        action="store_true", 
        help="Analyze existing transcription file (no video processing)"
    )
    parser.add_argument(
        "--output-json", 
        type=str, 
        help="Save enhanced analysis as JSON file"
    )
    
    args = parser.parse_args()
    
    # Handle Phi-3 enable/disable logic
    enable_phi3 = args.phi3 and not args.no_phi3
    
    if args.analyze_only:
        analyze_existing_transcription(args)
        return
    
    if not args.input_file:
        parser.error("Input file is required unless using --analyze-only")
    
    # Validate input file
    if not os.path.exists(args.input_file):
        logger.error(f"File not found: {args.input_file}")
        sys.exit(1)
    
    # Determine output paths
    base_name = os.path.splitext(args.input_file)[0]
    srt_output = args.output or f"{base_name}.srt"
    json_output = args.output_json or f"{base_name}_analysis.json"
    
    try:
        print(f"🎬 Starting enhanced transcription: {args.input_file}")
        print(f"🔧 Model: {args.model}, Language: {args.lang}")
        print(f"🧠 Phi-3 Brain: {'Enabled' if enable_phi3 else 'Disabled'}")
        print("-" * 50)
        
        if enable_phi3:
            # Use enhanced transcription with Phi-3
            result = transcribe_video_enhanced(
                args.input_file, 
                args.model, 
                args.lang, 
                enable_phi3=True,
                progress_callback=cli_progress_callback
            )
            
            # Save SRT file
            with open(srt_output, 'w', encoding='utf-8') as f:
                f.write(result["transcription"])
            
            # Display analysis results
            display_analysis_results(result)
            
            # Save JSON analysis if requested
            if args.output_json:
                with open(json_output, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                print(f"📊 Analysis saved: {json_output}")
            
            # Interactive mode
            if args.interactive:
                interactive_qa_mode(result["transcription"])
                
        else:
            # Basic transcription only
            srt_content = transcribe_video(
                args.input_file, 
                args.model, 
                args.lang, 
                cli_progress_callback
            )
            
            with open(srt_output, 'w', encoding='utf-8') as f:
                f.write(srt_content)
        
        print(f"\n✅ Transcription completed successfully!")
        print(f"📁 SRT file saved: {srt_output}")
        
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)

def analyze_existing_transcription(args):
    """Analyze an existing transcription file with Phi-3."""
    if not args.input_file or not os.path.exists(args.input_file):
        print("❌ Please provide a valid transcription file path")
        sys.exit(1)
    
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            transcription = f.read()
        
        print(f"🧠 Analyzing transcription: {args.input_file}")
        print("-" * 50)
        
        brain = Phi3Brain()
        analysis = brain.generate_metadata(transcription)
        
        result = {
            "transcription": transcription,
            "phi3_analysis": analysis,
            "source_file": args.input_file
        }
        
        display_analysis_results(result)
        
        # Save analysis if requested
        if args.output_json:
            with open(args.output_json, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"📊 Analysis saved: {args.output_json}")
        
        if args.interactive:
            interactive_qa_mode(transcription)
            
    except Exception as e:
        print(f"❌ Error analyzing transcription: {e}")
        sys.exit(1)

def display_analysis_results(result):
    """Display the Phi-3 analysis results in a formatted way."""
    if "phi3_analysis" not in result or "error" in result["phi3_analysis"]:
        print("⚠️  Phi-3 analysis unavailable")
        return
    
    analysis = result["phi3_analysis"]
    
    print("\n🧠 PHI-3 BRAIN ANALYSIS")
    print("=" * 50)
    
    # Summary
    if "summary" in analysis:
        print(f"📝 SUMMARY:\n{analysis['summary']}\n")
    
    # Key topics
    if "key_topics" in analysis and analysis["key_topics"]:
        print(f"🏷️  KEY TOPICS: {', '.join(analysis['key_topics'])}\n")
    
    # Quality assessment
    if "quality_assessment" in analysis:
        qa = analysis["quality_assessment"]
        if "quality_score" in qa:
            print(f"⭐ QUALITY SCORE: {qa['quality_score']}/10")
        if "confidence_level" in qa:
            print(f"🎯 CONFIDENCE: {qa['confidence_level']}")
        print()
    
    # Sentiment analysis
    if "sentiment_analysis" in analysis:
        sa = analysis["sentiment_analysis"]
        if "sentiment" in sa:
            print(f"😊 SENTIMENT: {sa['sentiment']}")
        if "tone" in sa:
            print(f"🎭 TONE: {sa['tone']}")
        print()
    
    # Suggested questions
    if "suggested_questions" in analysis and analysis["suggested_questions"]:
        print("❓ SUGGESTED QUESTIONS:")
        for i, q in enumerate(analysis["suggested_questions"], 1):
            print(f"   {i}. {q}")
        print()
    
    # Statistics
    if "word_count" in analysis:
        print(f"📊 STATISTICS:")
        print(f"   Words: {analysis['word_count']}")
        if "estimated_duration_minutes" in analysis:
            print(f"   Estimated duration: {analysis['estimated_duration_minutes']:.1f} minutes")
        print()

def interactive_qa_mode(transcription):
    """Interactive Q&A mode using Phi-3 brain."""
    print("\n🤖 INTERACTIVE Q&A MODE")
    print("=" * 30)
    print("Ask questions about the video content. Type 'quit' to exit.\n")
    
    brain = Phi3Brain()
    
    while True:
        try:
            question = input("❓ Your question: ").strip()
            
            if question.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not question:
                continue
            
            print("🧠 Thinking...")
            answer = brain.answer_question(transcription, question)
            print(f"💡 Answer: {answer}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}\n")


if __name__ == "__main__":
    main()
