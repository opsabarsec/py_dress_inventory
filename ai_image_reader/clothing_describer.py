import os
import base64
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

#
load_dotenv()
api_key = os.getenv("API_KEY")
from typing import List


def encode_image(image_path: str) -> str:
    """Encode image to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_image_files(folder_path: str) -> List[str]:
    """Get all image files from the folder."""
    image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
    image_files = []

    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"Folder '{folder_path}' does not exist")

    for file_path in folder.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in image_extensions:
            image_files.append(str(file_path))

    return sorted(image_files)


prompt_italiano = """Analizza queste immagini di abbigliamento e fornisci una
descrizione dettagliata dell'articolo di abbigliamento per una vendita su Vinted.
Includi informazioni su: stile e tipologia del capo, colore principale e eventuali colori secondari,
materiale e composizione (se visibile), vestibilità e taglia apparente, dettagli del design (bottoni, cerniere, tasche, stampe, ricami), 
condizioni dell'articolo (nuovo, come nuovo, buone condizioni, ecc.), marca se visibile, e qualsiasi caratteristica distintiva o difetto evidente. 
Se ci sono più immagini dello stesso capo, descrivilo in modo completo considerando tutti gli angoli mostrati.
Scrivi la descrizione in modo accattivante per attirare potenziali acquirenti."""


def describe_clothing_images(
    client: OpenAI, image_paths: List[str], prompt=prompt_italiano
) -> str:
    """Send images to OpenAI and get clothing descriptions."""

    # Prepare the messages
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt,
                }
            ],
        }
    ]
    # Add each image to the message
    for image_path in image_paths:
        try:
            base64_image = encode_image(image_path)
            file_extension = Path(image_path).suffix.lower()

            # Determine MIME type
            mime_type = "image/jpeg"
            if file_extension == ".png":
                mime_type = "image/png"
            elif file_extension == ".gif":
                mime_type = "image/gif"
            elif file_extension == ".webp":
                mime_type = "image/webp"

            messages[0]["content"].append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
                }
            )

            print(f"Added image: {Path(image_path).name}")

        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            continue

    # Make the API call
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Use gpt-4o for vision capabilities
            messages=messages,
            max_tokens=1000,
        )
        with open("description.txt", "w", encoding="utf-8") as f:
            f.write(response.choices[0].message.content)
        return response.choices[0].message.content

    except Exception as e:
        raise Exception(f"OpenAI API error: {e}")
