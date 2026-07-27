import gradio as gr

from src.credio.services.chat_service import CreditRiskChatSession

session = CreditRiskChatSession()

def respond(message, history):
    return session.send(message)

demo = gr.ChatInterface(
    fn=respond,
    title="CREDIO",
    description="Soy un agente evaluador de riesgo crediticio!",
    examples=["¿Que informacion tengo que enviarte?"],
)

if __name__ == "__main__":
    demo.launch()
