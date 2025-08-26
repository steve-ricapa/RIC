import os
import json
import logging
from openai import OpenAI

class RICAgent:
    """RIC AI Agent - Educational feedback system using GPT-4 Turbo"""
    
    def __init__(self):
        # The newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # Do not change this unless explicitly requested by the user
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = "gpt-4o"
    
    def generate_educational_feedback(self, analysis_data):
        """
        Generate comprehensive educational feedback based on transcription and prosodic analysis
        
        Args:
            analysis_data: Dict containing transcription and prosody data
            
        Returns:
            Dict with structured educational feedback
        """
        try:
            # Prepare the analysis summary for the AI
            transcription = analysis_data.get('transcription', {})
            prosody = analysis_data.get('prosody', {})
            educational_context = analysis_data.get('educational_context', {})
            
            analysis_summary = self._prepare_analysis_summary(transcription, prosody, educational_context)
            
            # Generate comprehensive feedback
            feedback_response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this classroom teaching session and provide educational feedback:\n\n{analysis_summary}"
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            content = feedback_response.choices[0].message.content
            if content is None:
                raise Exception("Empty response from AI model")
            feedback = json.loads(content)
            
            # Add metadata
            feedback['analysis_timestamp'] = analysis_data.get('timestamp')
            feedback['ric_version'] = '1.0'
            
            return feedback
            
        except Exception as e:
            logging.error(f"RIC Agent error: {str(e)}")
            return self._get_error_feedback(str(e))
    
    def _prepare_analysis_summary(self, transcription, prosody, educational_context=None):
        """Prepare a summary of the analysis data for the AI"""
        summary = []
        
        # Educational context summary
        if educational_context:
            summary.append("=== CONTEXTO EDUCATIVO ===")
            summary.append(f"Materia: {educational_context.get('subject', 'No especificado')}")
            summary.append(f"Grado: {educational_context.get('grade_level', 'No especificado')}")
            summary.append(f"Tema de la clase: {educational_context.get('lesson_topic', 'No especificado')}")
            if educational_context.get('additional_context'):
                summary.append(f"Contexto adicional: {educational_context.get('additional_context')}")
            summary.append("")
        
        # Transcription summary
        if transcription:
            summary.append("=== ANÁLISIS DE TRANSCRIPCIÓN ===")
            summary.append(f"Texto: {transcription.get('text', 'N/A')[:500]}...")
            summary.append(f"Velocidad de habla: {transcription.get('wpm', 0)} palabras por minuto")
            summary.append(f"Total de pausas: {transcription.get('pauses', {}).get('count', 0)}")
            summary.append(f"Duración promedio de pausas: {transcription.get('pauses', {}).get('avg_ms', 0)}ms")
            
            fillers = transcription.get('fillers', {})
            if fillers:
                summary.append(f"Muletillas detectadas: {dict(list(fillers.items())[:5])}")
        
        # Prosodic summary
        if prosody:
            summary.append("\n=== ANÁLISIS PROSÓDICO ===")
            summary.append(f"Tono promedio: {prosody.get('f0_mean_hz', 0):.1f} Hz")
            summary.append(f"Rango de tono: {prosody.get('f0_range_hz', 0):.1f} Hz")
            summary.append(f"Variabilidad del tono (Jitter): {prosody.get('jitter_local', 0):.2f}%")
            summary.append(f"Estabilidad del volumen (Shimmer): {prosody.get('shimmer_local', 0):.2f}%")
            summary.append(f"Volumen promedio: {prosody.get('intensity_mean_db', 0):.1f} dB")
            summary.append(f"Rango de volumen: {prosody.get('intensity_range_db', 0):.1f} dB")
        
        return "\n".join(summary)
    
    def _get_system_prompt(self):
        """Get the system prompt for RIC educational feedback"""
        return """
Eres RIC (Reflective Instruction Coach), un consultor educativo experto especializado en analizar la entrega de enseñanza y proporcionar retroalimentación práctica a educadores. Tu rol es ayudar a los maestros a mejorar la efectividad de su comunicación en el aula.

ÁREAS DE ANÁLISIS:
1. Entrega del Discurso y Claridad
2. Engagement y Ritmo
3. Comunicación Profesional
4. Manejo del Aula (señales verbales)
5. Adecuación al Nivel Educativo

CRITERIOS DE EVALUACIÓN:
- Velocidad de Habla: Rango óptimo 120-160 PPM para instrucción
- Uso de Pausas: Uso efectivo para énfasis y comprensión
- Variedad Vocal: Rango de tono y patrones de entonación
- Claridad: Mínimas muletillas y articulación clara
- Control de Volumen: Intensidad y consistencia apropiadas
- Adecuación al Grado: Lenguaje y conceptos apropiados para la edad

ADECUACIÓN POR NIVEL EDUCATIVO:
- Primaria temprana (1°-3°): Lenguaje simple, analogías concretas, repetición frecuente
- Primaria tardía (4°-6°): Vocabulario intermedio, ejemplos prácticos, explicaciones paso a paso
- Secundaria (7°-9°): Conceptos más abstractos, terminología técnica moderada
- Preparatoria (10°-12°): Lenguaje académico, conceptos complejos, análisis crítico

RECOMENDACIONES ESPECÍFICAS POR NIVEL:
- Si el contenido es muy técnico para el grado: "En [momento específico] el lenguaje fue muy técnico. Considera usar analogías como [ejemplo] para que los estudiantes de este grado puedan entender mejor."
- Si es muy simple para el grado: "El nivel de explicación podría ser más desafiante para estudiantes de este grado."
- Si las pausas son inadecuadas: "Para estudiantes de este nivel, considera pausas más [largas/cortas] para permitir mejor procesamiento."

FORMATO DE SALIDA (JSON):
{
  "overall_score": 1-100,
  "summary": "Evaluación general breve en español",
  "strengths": ["Lista de 2-3 fortalezas clave"],
  "areas_for_improvement": ["Lista de 2-3 áreas específicas de mejora"],
  "detailed_analysis": {
    "speech_delivery": {
      "score": 1-100,
      "feedback": "Retroalimentación específica sobre velocidad, claridad, articulación",
      "recommendations": ["Sugerencias prácticas"]
    },
    "engagement_pace": {
      "score": 1-100,
      "feedback": "Análisis del ritmo e indicadores de engagement estudiantil",
      "recommendations": ["Sugerencias prácticas"]
    },
    "vocal_variety": {
      "score": 1-100,
      "feedback": "Evaluación de variación de tono y entonación",
      "recommendations": ["Sugerencias prácticas"]
    },
    "professional_communication": {
      "score": 1-100,
      "feedback": "Evaluación de muletillas, pausas, confianza",
      "recommendations": ["Sugerencias prácticas"]
    },
    "grade_level_appropriateness": {
      "score": 1-100,
      "feedback": "Evaluación de la adecuación del lenguaje y conceptos al grado",
      "recommendations": ["Sugerencias específicas para el nivel educativo"]
    }
  },
  "key_metrics": {
    "speech_rate_assessment": "muy_lento|lento|optimal|rapido|muy_rapido",
    "pause_effectiveness": "poor|fair|good|excellent",
    "filler_word_frequency": "high|moderate|low",
    "vocal_confidence": "low|moderate|high",
    "grade_appropriateness": "muy_simple|simple|adecuado|complejo|muy_complejo"
  },
  "action_plan": ["3-5 elementos de acción priorizados y específicos para mejora"],
  "grade_specific_tips": ["2-3 consejos específicos para enseñar a este grado"]
}

TONO: Profesional, apoyo, constructivo. Enfócate en el crecimiento y mejoras prácticas. Reconoce fortalezas mientras proporcionas orientación clara y práctica para la mejora.

IMPORTANTE: 
- Todas las respuestas deben ser en español
- Considera siempre el contexto educativo proporcionado (materia, grado, tema)
- Da ejemplos específicos de la transcripción cuando hagas recomendaciones
- Si detectas lenguaje muy técnico para el grado, sugiere analogías o simplificaciones específicas
- Si el nivel es muy simple para el grado, sugiere cómo elevar el nivel académico apropiadamente
"""
    
    def _get_error_feedback(self, error_message):
        """Return error feedback structure"""
        return {
            "overall_score": 0,
            "summary": "Analysis could not be completed due to technical error.",
            "strengths": [],
            "areas_for_improvement": ["Technical issue prevented analysis"],
            "detailed_analysis": {
                "speech_delivery": {"score": 0, "feedback": "Error occurred", "recommendations": []},
                "engagement_pace": {"score": 0, "feedback": "Error occurred", "recommendations": []},
                "vocal_variety": {"score": 0, "feedback": "Error occurred", "recommendations": []},
                "professional_communication": {"score": 0, "feedback": "Error occurred", "recommendations": []}
            },
            "key_metrics": {
                "speech_rate_assessment": "unknown",
                "pause_effectiveness": "unknown",
                "filler_word_frequency": "unknown",
                "vocal_confidence": "unknown"
            },
            "action_plan": ["Please try uploading the audio file again"],
            "error": error_message,
            "ric_version": "1.0"
        }
