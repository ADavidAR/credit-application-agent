import gradio as gr

def respond(message, history):
    # Simple eco-bot logic
    if "hola" in message.lower():
        return "Holaa! Como te ayuden?"
    
    return f"Dijiste: '{message}'. todavía no soy tan inteligente como para responder apropiadamente"

demo = gr.ChatInterface(
    fn=respond,
    title="CREDIO",
    description="Soy un agente evaluador de riesgo crediticio!",
    examples=["¿Que informacion tengo que enviarte?"],
)
