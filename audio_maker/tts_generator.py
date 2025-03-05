import os
import logging
from typing import List, Tuple, Optional, Generator
import soundfile as sf
import numpy as np
from kokoro import KPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("tts_generator")

# Constants for TTS configuration
DEFAULT_LANG_CODE = 'a'  # American English
DEFAULT_VOICE = 'af_heart'  # Default voice
DEFAULT_SPEED = 1.0
DEFAULT_SAMPLE_RATE = 24000

class TTSGenerator:
    """Class for Text-to-Speech generation using the Kokoro model."""
    
    def __init__(
        self, 
        lang_code: str = DEFAULT_LANG_CODE, 
        voice: str = DEFAULT_VOICE, 
        speed: float = DEFAULT_SPEED,
        sample_rate: int = DEFAULT_SAMPLE_RATE
    ):
        """
        Initialize the TTS Generator.
        
        Args:
            lang_code: Language code ('a' for American English, 'b' for British English, etc.)
            voice: Voice ID to use
            speed: Speech speed factor (1.0 is normal)
            sample_rate: Audio sample rate in Hz
        """
        logger.info(f"Initializing TTS Generator with lang_code={lang_code}, voice={voice}")
        self.pipeline = KPipeline(lang_code=lang_code)
        self.voice = voice
        self.speed = speed
        self.sample_rate = sample_rate
        logger.info("TTS Generator initialized successfully")
    
    def generate_audio(
        self, 
        text: str, 
        split_pattern: str = r'\n+'
    ) -> Generator[Tuple[str, str, np.ndarray], None, None]:
        """
        Generate audio from text using Kokoro TTS.
        
        Args:
            text: The text to convert to speech
            split_pattern: Pattern to split text into segments
            
        Returns:
            Generator yielding tuples of (graphemes, phonemes, audio)
        """
        logger.info(f"Generating audio for text of length {len(text)}")
        return self.pipeline(
            text,
            voice=self.voice,
            speed=self.speed,
            split_pattern=split_pattern
        )
    
    def generate_and_save(
        self, 
        text: str, 
        output_dir: str, 
        filename: str,
        split_pattern: str = r'\n+',
        combine_audio: bool = True
    ) -> List[str]:
        """
        Generate audio from text and save to files.
        
        Args:
            text: The text to convert to speech
            output_dir: Directory to save audio files
            filename: Base filename for the output files
            split_pattern: Pattern to split text into segments
            combine_audio: Whether to combine all segments into a single file
            
        Returns:
            List of paths to the generated audio files
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Remove extension from filename if present
        base_filename = os.path.splitext(filename)[0]
        
        # Generate audio segments
        audio_segments = []
        output_files = []
        
        try:
            for i, (gs, ps, audio) in enumerate(self.generate_audio(text, split_pattern)):
                segment_filename = f"{base_filename}_segment_{i}.wav"
                segment_path = os.path.join(output_dir, segment_filename)
                
                # Save individual segment
                # sf.write(segment_path, audio, self.sample_rate)
                # output_files.append(segment_path)
                
                # Store audio for potential combination
                if combine_audio:
                    audio_segments.append(audio)
                
                logger.info(f"Saved audio segment {i} to {segment_path}")
            
            # Combine segments if requested
            if combine_audio and audio_segments:
                combined_audio = np.concatenate(audio_segments)
                combined_filename = f"{base_filename}.wav"
                combined_path = os.path.join(output_dir, combined_filename)
                
                # Save combined audio
                sf.write(combined_path, combined_audio, self.sample_rate)
                output_files.append(combined_path)
                
                logger.info(f"Saved combined audio to {combined_path}")
            
            return output_files
            
        except Exception as e:
            logger.error(f"Error generating audio: {e}")
            raise

def get_available_voices() -> List[str]:
    """
    Get a list of available built-in voices.
    
    Returns:
        List of available voice IDs
    """
    return [
        "af_heart",  # Default voice
        "af_calm",
        "af_bright",
        "af_serious"
    ]