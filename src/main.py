from bs4 import BeautifulSoup
from io import StringIO
from claimsExtractor import process_json_files
import matplotlib.pyplot as plt
import pandas as pd
import json
import os
import re

def clean_latex(text):
    # Rimuove comandi LaTeX come \textbf{}, \frac{}, ecc.
    text = re.sub(r'\\[a-zA-Z]+\{.*?\}', '', text)  # Rimuove \comando{...}
    text = re.sub(r'\\[a-zA-Z]+', '', text)  # Rimuove comandi come \textbf
    text = re.sub(r'\$', '', text)  # Rimuove il simbolo $
    return text


def convert_to_df(html_table):
    # extract table with BeautifulSoup
    soup = BeautifulSoup(html_table, 'html.parser')

    for footnote in soup.find_all("span", class_="ltx_note ltx_role_footnote"):
        footnote.decompose()  # removes span tag
    for math_element in soup.find_all("math", class_="ltx_Math"):
        math_element.decompose()  # removes math tag

    table = soup.find("table")

    # convert table to pandas dataframe
    df:pd.DataFrame = pd.read_html(StringIO(str(table)))[0]

    # cleaning latex commands
    df = df.map(lambda x: clean_latex(str(x)))

    # removes first numbered row if present
    first_row = df.iloc[0].apply(pd.to_numeric, errors='coerce')

    is_numeric_index = first_row.index.map(lambda x: isinstance(x, (int, float)))
    is_consecutive = False
    if is_numeric_index.all():
        is_consecutive = all(first_row.index[i] == first_row.index[i-1] + 1 for i in range(1, len(first_row.index)))
    if is_consecutive:
        df.columns = df.iloc[0]
        df = df.drop(index=0).reset_index(drop=True)

    return df

def save_table_as_image(df:pd.DataFrame, path:str):
    fig, ax = plt.subplots(figsize=(6, 2))  # Imposta dimensioni personalizzate
    ax.axis('off')  # Rimuove assi

    # Aggiungere la tabella
    df = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')

    # Salva come immagine
    plt.savefig(path, bbox_inches='tight', dpi=300)
    plt.close(fig)

def save_table_as_json(df:pd.DataFrame, caption:str, references: list, path:str):
    # extract header of pandas dataframe
    header = df.columns.tolist()

    # 
    df_as_json = [header]
    rows_as_lists = df.apply(lambda row: row.astype(str).tolist(), axis=1)

    for row_list in rows_as_lists:
        df_as_json.append(row_list)

    json_content = {
        "table": df_as_json,
        "caption": caption,
        "references": references
    }

    with open(path, "w") as file:
        json.dump(json_content, file, indent=4)


def generate_json():
    path = "../raw"
    raw_files = os.listdir(path)
    raw_files.sort()

    for filename in raw_files:
        json_file = json.load(open(f"{path}/{filename}"))
        file_id = f"{filename.split('.')[0]}" + "." + f"{filename.split('.')[1]}"
        for i, table_id in enumerate(json_file.keys()):
            # get table tag
            html_table = json_file[table_id]["table"]
            caption = json_file[table_id]["caption"]
            references = json_file[table_id]["references"]

            # convert to dataframe
            df = convert_to_df(html_table)
            #
            #df.to_json(f"../data/json/{file_id}-{table_id}.json", index=False, indent=4)
            df.to_csv(f"../data/csv/{file_id}-{table_id}.csv", index=False)
            save_table_as_image(df, f"../data/images/{file_id}-{table_id}.png")
            save_table_as_json(df,caption, references, f"../data/json/{file_id}_{i + 1}.json")


if __name__ == "__main__":
    generate_json()
    process_json_files(input_dir='../data/json',
                       output_dir='../data/claims',
                       model_name="llama3.2",
                       prompt_file_path='prompt.txt')
    