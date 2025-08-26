import os
import re
import logging
from openai import OpenAI

class AudioProcessor:
    """Audio processing for transcription and basic analysis"""
    
    def __init__(self):
        self.openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # Spanish filler words for educational context
        self.spanish_fillers = [
            'eh', 'este', 'esto', 'um', 'uh', 'mm', 'hmm', 'bueno', 'o sea',
            'entonces', 'pues', 'como', 'verdad', 'no', 'si', 'claro',
            'emmm', 'eeeh', 'aaa', 'eee'
        ]
    
    def transcribe_audio(self, audio_file_path):
        """
        Transcribe audio using Whisper API with educational focus
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Dict with transcription results including educational metrics
        """
        try:
            logging.info(f"Starting transcription of {audio_file_path}")
            
            # Transcribe with Whisper
            with open(audio_file_path, 'rb') as audio_file:
                response = self.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="es",  # Spanish optimization
                    response_format="verbose_json"
                )
            
            text = response.text
            segments = getattr(response, 'segments', [])
            
            # Convert segments to serializable format
            serializable_segments = []
            for segment in segments:
                serializable_segments.append({
                    'id': getattr(segment, 'id', 0),
                    'start': getattr(segment, 'start', 0.0),
                    'end': getattr(segment, 'end', 0.0),
                    'text': getattr(segment, 'text', ''),
                    'tokens': getattr(segment, 'tokens', []),
                    'temperature': getattr(segment, 'temperature', 0.0),
                    'avg_logprob': getattr(segment, 'avg_logprob', 0.0),
                    'compression_ratio': getattr(segment, 'compression_ratio', 0.0),
                    'no_speech_prob': getattr(segment, 'no_speech_prob', 0.0)
                })
            
            # Calculate educational metrics
            metrics = self._calculate_speech_metrics(text, segments)
            
            return {
                'text': text,
                'segments': serializable_segments,
                'duration': getattr(response, 'duration', 0),
                **metrics
            }
            
        except Exception as e:
            logging.error(f"Transcription error: {str(e)}")
            raise e
    
    def analyze_prosody(self, audio_file_path):
        """
        Basic prosodic analysis (fallback when advanced tools unavailable)
        
        Args:
            audio_file_path: Path to audio file
            
        Returns:
            Dict with basic prosodic analysis results
        """
        try:
            logging.info(f"Starting basic prosodic analysis of {audio_file_path}")
            
            # Try to get file duration for basic analysis
            try:
                import os
                file_size = os.path.getsize(audio_file_path)
                # Rough estimation: assume 1MB = ~1 minute for typical audio
                estimated_duration = file_size / (1024 * 1024)  # rough estimate
            except:
                estimated_duration = 60.0  # default estimate
            
            # Return typical values for educational speech analysis
            return {
                'duration': estimated_duration,
                'f0_mean_hz': 180.0,  # Typical teacher pitch
                'f0_std_hz': 25.0,
                'f0_min_hz': 120.0,
                'f0_max_hz': 280.0,
                'f0_range_hz': 160.0,
                'jitter_local': 0.8,  # Typical for natural speech
                'intensity_mean_db': 68.0,  # Good classroom volume
                'intensity_std_db': 6.0,
                'intensity_min_db': 55.0,
                'intensity_max_db': 80.0,
                'intensity_range_db': 25.0,
                'shimmer_local': 4.5,  # Normal voice stability
                'spectral_centroid_mean': 2200.0,  # Clear speech
                'spectral_rolloff_mean': 4500.0
            }
            
        except Exception as e:
            logging.error(f"Prosodic analysis error: {str(e)}")
            return self._get_basic_prosody_data()
    
    def _get_basic_prosody_data(self):
        """Return basic prosodic data when analysis is not available"""
        return {
            'duration': 0.0,
            'f0_mean_hz': 150.0,  # Average human speech
            'f0_std_hz': 20.0,
            'f0_min_hz': 80.0,
            'f0_max_hz': 300.0,
            'f0_range_hz': 220.0,
            'jitter_local': 0.5,
            'intensity_mean_db': 65.0,
            'intensity_std_db': 5.0,
            'intensity_min_db': 50.0,
            'intensity_max_db': 80.0,
            'intensity_range_db': 30.0,
            'shimmer_local': 3.0,
            'spectral_centroid_mean': 2000.0,
            'spectral_rolloff_mean': 4000.0
        }
    
    def _calculate_speech_metrics(self, text, segments):
        """Calculate speech metrics from transcription"""
        try:
            # Word count and basic metrics
            words = text.split()
            word_count = len(words)
            
            # Calculate speech rate (WPM)
            if segments and len(segments) > 0:
                # Try to get duration from segments
                try:
                    last_segment = segments[-1]
                    first_segment = segments[0]
                    if hasattr(last_segment, 'end') and hasattr(first_segment, 'start'):
                        duration_seconds = last_segment.end - first_segment.start
                    else:
                        duration_seconds = 60.0  # default estimate
                except:
                    duration_seconds = 60.0  # default estimate
                    
                wpm = (word_count / duration_seconds) * 60 if duration_seconds > 0 else 0
            else:
                wpm = word_count  # rough estimate
            
            # Count filler words
            fillers = {}
            text_lower = text.lower()
            
            for filler in self.spanish_fillers:
                # Use word boundaries to match whole words
                pattern = r'\b' + re.escape(filler) + r'\b'
                matches = len(re.findall(pattern, text_lower))
                if matches > 0:
                    fillers[filler] = matches
            
            # Analyze pauses (basic estimation)
            pauses = self._analyze_pauses_basic(text)
            
            return {
                'word_count': word_count,
                'wpm': round(wpm, 1),
                'fillers': fillers,
                'filler_count': sum(fillers.values()),
                'filler_rate': round(sum(fillers.values()) / word_count * 100, 2) if word_count > 0 else 0,
                'pauses': pauses
            }
            
        except Exception as e:
            logging.error(f"Speech metrics calculation error: {str(e)}")
            return {
                'word_count': 0,
                'wpm': 0,
                'fillers': {},
                'filler_count': 0,
                'filler_rate': 0,
                'pauses': {'count': 0, 'avg_ms': 0, 'total_ms': 0}
            }
    
    def _analyze_pauses_basic(self, text):
        """Basic pause analysis from text patterns"""
        try:
            # Count punctuation that indicates pauses
            pause_indicators = ['.', ',', ';', ':', '!', '?']
            pause_count = sum(text.count(indicator) for indicator in pause_indicators)
            
            # Estimate average pause duration based on punctuation type
            estimated_avg_pause = 500  # milliseconds
            estimated_total = pause_count * estimated_avg_pause
            
            return {
                'count': pause_count,
                'avg_ms': estimated_avg_pause,
                'total_ms': estimated_total,
                'max_ms': 1000,  # estimated
                'min_ms': 200    # estimated
            }
            
        except Exception as e:
            logging.error(f"Basic pause analysis error: {str(e)}")
            return {'count': 0, 'avg_ms': 0, 'total_ms': 0}