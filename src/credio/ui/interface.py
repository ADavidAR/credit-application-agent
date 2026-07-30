import gradio as gr

from credio.services.chat import CreditRiskChatService
from  credio.services.prediction_client import ApiPredictionClient

session = CreditRiskChatService(ApiPredictionClient())

def respond(message, history):
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
