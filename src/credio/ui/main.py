import os

from credio.ui.interface import demo


def main() -> None:
    """
    Punto de entrada de la interfaz. Levanta la app de Gradio ("demo"),
    usando host y puerto configurables por variable de entorno
    ("UI_HOST", "UI_PORT") para poder dockerizarla aparte.
    """
    demo.launch(
        server_name=os.environ.get("UI_HOST", "0.0.0.0"),
        server_port=int(os.environ.get("UI_PORT", "7860")),
    )


if __name__ == "__main__":
    main()
