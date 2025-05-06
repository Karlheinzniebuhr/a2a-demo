# A2A Protocol Demo

This project demonstrates the Agent2Agent (A2A) protocol using a simple interaction between a Planning Agent and an Execution Agent. The demo focuses on the `tasks/send` method, showcasing how agents can exchange messages and update a shared task history.

## A2A Protocol Overview

The Agent2Agent (A2A) protocol facilitates communication between independent AI agents, enabling them to collaborate and work together regardless of their underlying frameworks or vendors. It provides a common language for agents to understand each other's capabilities and negotiate interactions. Key concepts include Agent Cards for discovery, A2A Servers and Clients for communication, and Tasks as the central unit of work with a history of Messages and optional Artifacts.

## Project Files

-   `a2a_models.py`: Pydantic models defining the A2A protocol's data structures, ensuring schema compliance.
-   `execution_agent.py`: A simple Flask web server acting as the Execution Agent. It receives A2A `tasks/send` requests, processes messages using a Gemini LLM, updates the task history, and returns A2A responses.
-   `planning_agent.py`: A Python script acting as the Planning Agent client. It initiates tasks, sends A2A `tasks/send` requests to the Execution Agent, processes responses, and logs the communication. It uses a Gemini LLM for planning the next steps.
-   `requirements.txt`: Lists the necessary Python dependencies (`flask`, `requests`, `pydantic`, `google-generativeai`, `python-dotenv`).
-   `communication_log.txt`: Logs the raw JSON payloads of A2A requests and responses exchanged between the agents, providing a clear record of the protocol in action.

## Setup

1.  Clone this repository.
2.  Navigate to the project directory in your terminal.
3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Set your Gemini API key as an environment variable named `GEMINI_API_KEY`. You can create a `.env` file in the project root with the line `GEMINI_API_KEY=your_api_key_here`.

## Running the Demo

1.  Open two separate terminal windows in the project directory.
2.  In the first terminal, start the Execution Agent server:
    ```bash
    python execution_agent.py
    ```
    The server will start and listen on `http://localhost:5000`.
3.  In the second terminal, run the Planning Agent client:
    ```bash
    python planning_agent.py
    ```
    The Planning Agent will initiate a task, communicate with the Execution Agent, and log the process.
4.  Observe the output in both terminals and the `communication_log.txt` file to see the A2A messages being exchanged.

## Communication Example (`tasks/send`)

This demo illustrates the `tasks/send` method. The Planning Agent sends a request to the Execution Agent, including a message and a task ID. The Execution Agent processes the message, adds its response to the task history, and returns the updated task object in the response.

**Planning Agent Request Example:**

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

**Execution Agent Response Example:**

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

Notice how the `history` field in the `Task` object within the response contains both the original message from the Planning Agent (role "user") and the response from the Execution Agent (role "agent").

## Spanish Version

---

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
