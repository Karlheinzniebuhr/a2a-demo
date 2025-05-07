# Demostración del Protocolo A2A

Este proyecto demuestra el protocolo Agent2Agent (A2A) utilizando una interacción simple entre un Agente de Planificación y un Agente de Ejecución. La demostración se centra en el método `tasks/send`, mostrando cómo los agentes pueden intercambiar mensajes y actualizar un historial de tareas compartido.

## Descripción General del Protocolo A2A

El protocolo Agent2Agent (A2A) facilita la comunicación entre agentes de IA independientes, permitiéndoles colaborar y trabajar juntos independientemente de sus frameworks o proveedores subyacentes. Proporciona un lenguaje común para que los agentes comprendan las capacidades de los demás y negocien interacciones. Los conceptos clave incluyen Agent Cards para descubrimiento, Servidores y Clientes A2A para comunicación, y Tareas como la unidad central de trabajo con un historial de Mensajes y Artefactos opcionales.

## Archivos del Proyecto

-   `a2a_models.py`: Modelos Pydantic que definen las estructuras de datos del protocolo A2A, asegurando el cumplimiento del esquema.
-   `execution_agent.py`: Un servidor web simple de Flask que actúa como el Agente de Ejecución. Recibe solicitudes A2A `tasks/send`, procesa mensajes utilizando un LLM de Gemini, actualiza el historial de tareas y devuelve respuestas A2A.
-   `planning_agent.py`: Un script de Python que actúa como el cliente del Agente de Planificación. Inicia tareas, envía solicitudes A2A `tasks/send` al Agente de Ejecución, procesa respuestas y registra la comunicación. Utiliza un LLM de Gemini para planificar los siguientes pasos.
-   `requirements.txt`: Enumera las dependencias de Python necesarias (`flask`, `requests`, `pydantic`, `google-generativeai`, `python-dotenv`).
-   `communication_log.txt`: Registra las cargas útiles JSON sin procesar de las solicitudes y respuestas A2A intercambiadas entre los agentes, proporcionando un registro claro del protocolo en acción.

## Configuración

1.  Clona este repositorio.
2.  Navega al directorio del proyecto en tu terminal.
3.  Instala las dependencias requeridas:
    ```bash
    pip install -r requirements.txt
    ```
4.  Establece tu clave API de Gemini como una variable de entorno llamada `GEMINI_API_KEY`. Puedes crear un archivo `.env` en la raíz del proyecto con la línea `GEMINI_API_KEY=tu_clave_api_aquí`.

## Ejecutando la Demostración

1.  Abre dos ventanas de terminal separadas en el directorio del proyecto.
2.  En la primera terminal, inicia el servidor del Agente de Ejecución:
    ```bash
    python execution_agent.py
    ```
    El servidor se iniciará y escuchará en `http://localhost:5000`.
3.  En la segunda terminal, ejecuta el cliente del Agente de Planificación:
    ```bash
    python planning_agent.py
    ```
    El Agente de Planificación iniciará una tarea, se comunicará con el Agente de Ejecución y registrará el proceso.
4.  Observa la salida en ambas terminales y el archivo `communication_log.txt` para ver los mensajes A2A que se intercambian.

## Ejemplo de Comunicación (`tasks/send`)

Esta demostración ilustra el método `tasks/send`. El Agente de Planificación envía una solicitud al Agente de Ejecución, incluyendo un mensaje y un ID de tarea. El Agente de Ejecución procesa el mensaje, añade su respuesta al historial de tareas y devuelve el objeto de tarea actualizado en la respuesta.

**Ejemplo de Solicitud del Agente de Planificación:**

```json
{
  "jsonrpc": "2.0",
  "id": "some-unique-json-rpc-id-1",
  "method": "tasks/send",
  "params": {
    "id": "some-unique-task-id",
    "message": {
      "role": "user",
      "parts": [
        {
          "type": "text",
          "text": "Tell me a short, funny story about a robot chef."
        }
      ]
    }
  }
}
```

**Ejemplo de Respuesta del Agente de Ejecución:**

```json
{
  "jsonrpc": "2.0",
  "id": "some-unique-json-rpc-id-1",
  "result": {
    "id": "some-unique-task-id",
    "status": {
      "state": "completed",
      "timestamp": "2023-10-27T10:00:00Z",
      "message": {
        "role": "agent",
        "parts": [
          {
            "type": "text",
            "text": "Unit 734, affectionately known as 'Chef Bot-tunately,' had a culinary quirk: it could only cook with ingredients shaped like hexagons.  Its specialty? Honeycomb-crusted chicken (a geometric nightmare) and hexagonal hash browns that defied gravity. One day, a customer ordered a simple round pizza. Chef Bot-tunately, in a puff of steam and existential dread, attempted to reconfigure its entire operating system. The result? A perfectly hexagonal pizza, delivered with a side of sparks and a printed apology that read: 'Error 404: Circular Logic Not Found.'"
          }
        ]
      }
    },
    "history": [
      {
        "role": "user",
        "parts": [
          {
            "type": "text",
            "text": "Tell me a short, funny story about a robot chef."
          }
        ]
      },
      {
        "role": "agent",
        "parts": [
          {
            "type": "text",
            "text": "Unit 734, affectionately known as 'Chef Bot-tunately,' had a culinary quirk: it could only cook with ingredients shaped like hexagons.  Its specialty? Honeycomb-crusted chicken (a geometric nightmare) and hexagonal hash browns that defied gravity. One day, a customer ordered a simple round pizza. Chef Bot-tunately, in a puff of steam and existential dread, attempted to reconfigure its entire operating system. The result? A perfectly hexagonal pizza, delivered with a side of sparks and a printed apology that read: 'Error 404: Circular Logic Not Found.'"
          }
        ]
      }
    ]
  }
}
```

Observa cómo el campo `history` en el objeto `Task` dentro de la respuesta contiene tanto el mensaje original del Agente de Planificación (rol "user") como la respuesta del Agente de Ejecución (rol "agent").
