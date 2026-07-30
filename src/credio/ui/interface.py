import gradio as gr

from credio.services.chat import CreditRiskChatService
from  credio.services.prediction_client import ApiPredictionClient

session = CreditRiskChatService(ApiPredictionClient())

def respond(message, history):
    """
    Callback del "ChatInterface" de Gradio. Envía el mensaje del usuario
    a la sesión de "CreditRiskChatService" compartida y devuelve su respuesta.

    Args:
        message: mensaje escrito por el usuario en la interfaz.
        history: historial de turnos que gestiona Gradio (no se usa; el
            estado real de la conversación esta contenido en "session").

    Returns:
        Texto de respuesta del asistente.
    """
    return session.send(message)

demo = gr.ChatInterface(
    fn=respond,
    title="CREDIO",
    description="Soy un agente evaluador de riesgo crediticio!",
    examples=["Hola, quisieras que evaluaras mi riesgo crediticio."],
    autofocus=True
)

if __name__ == "__main__":
    demo.launch()
