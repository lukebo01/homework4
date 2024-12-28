from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import pandas as pd
import ollama
import json
import os

def read_prompt_template(prompt_file_path):
    """
    Legge il template del prompt da un file con codifica UTF-8 e gestione degli errori.
    Args:
        prompt_file_path (str): Percorso del file di testo contenente il template del prompt.
    Returns:
        str: Il contenuto del file del template del prompt, o None se si verifica un errore.
    """
    try:
        with open(prompt_file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Errore: File non trovato al percorso '{prompt_file_path}'")
        return None
    except Exception as e:
        print(f"Errore durante la lettura del file: {e}")
        return None


def interact_with_llm(table_json, model_name, prompt_template):
    """
    Interagisce con un modello linguistico locale (LLM) per generare delle affermazioni.

    Args:
        table_json (dict): Dati JSON tabellari.
        model_name (str): Nome del modello LLM da utilizzare.
        prompt_template (str): Template del prompt.

    Returns:
        dict: Affermazioni generate dall'LLM, o None in caso di errore.
    """
    # Converti il JSON della tabella in una stringa per il prompt
    table_json_str = json.dumps(table_json, indent=4)

    # Crea il prompt completo inserendo la stringa JSON nel template
    full_prompt = prompt_template + "\n" + table_json_str

    # Usa Ollama per inviare il prompt al modello
    try:
        # Costruisci la struttura corretta del messaggio per ollama.chat
        messages = [{"role": "user", "content": full_prompt}]
        response = ollama.chat(model=model_name, messages=messages)
        print("Risposta da LLM:", response)  # Stampa la risposta del modello
    except Exception as e:
        print("Errore durante l'invio del prompt a LLM:", str(e))
        return None

    # Estrai la risposta JSON
    try:
        claims = json.loads(response['message']['content'])
        return claims
    except json.JSONDecodeError as e:
        print("Impossibile analizzare l'output dell'LLM come JSON:", str(e))
        return None

def process_json_files(input_dir, output_dir, model_name, prompt_file_path):
    """
    Processa più file JSON, estrae le affermazioni usando un modello LLM locale e salva i risultati.

    Args:
        input_dir (str): Directory contenente i file JSON.
        output_dir (str): Directory dove i risultati verranno salvati.
        model_name (str): Nome del modello LLM da usare.
        prompt_file_path (str): Percorso del file di template del prompt.
    """
    # Leggi il template del prompt dal file
    prompt_template = read_prompt_template(prompt_file_path)
    if not prompt_template:  # Se la lettura del file fallisce, esci dalla funzione
        return

    # Assicura che la directory di output esista
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Processa ogni file JSON nella directory di input
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            file_path = os.path.join(input_dir, filename)
            try:
                 with open(file_path, 'r', encoding='utf-8') as file:
                     table_json = json.load(file)
            except FileNotFoundError:
                 print(f"Errore: File non trovato al percorso '{file_path}'")
                 continue  # passa al prossimo file
            except json.JSONDecodeError as e:
                 print(f"Errore: Impossibile analizzare il file JSON '{filename}': {e}")
                 continue  # passa al prossimo file
            except Exception as e:
                 print(f"Errore inatteso durante la lettura del file '{filename}': {e}")
                 continue  # passa al prossimo file

            # Genera le affermazioni usando l'LLM
            claims = interact_with_llm(table_json, model_name, prompt_template)

            if claims is not None:
               # Salva l'output nella directory di output specificata
               output_filename = filename.replace('.json', '_claims.json')
               output_file_path = os.path.join(output_dir, output_filename)
               try:
                    with open(output_file_path, 'w', encoding='utf-8') as output_file:
                         json.dump(claims, output_file, indent=4)
                    print(f"Elaborato {filename} e affermazioni salvate in {output_file_path}")
               except Exception as e:
                     print(f"Errore durante il salvataggio del file '{output_file_path}': {e}")
            else:
                print(f"Errore durante l'estrazione di affermazioni per {filename}. Nessun file salvato.")