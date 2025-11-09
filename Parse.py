import xml.etree.ElementTree as ET
import re
import os
import random
import genanki
import shutil

from bs4 import BeautifulSoup
from time import sleep
from pathlib import Path
from utils import convert_blobs, clean_html

media_directory = 'media_temp'
algo_decks_folder_name = 'algo_decks'

# Create output folder if does not exist and assign to output path variable
output_path = Path('output/')
output_path.mkdir(parents=True, exist_ok=True)
output_path = output_path.absolute()

def read_algo(xml_path, blob_map):
    with open(xml_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')

    cards = []

    for card in soup.find_all('card'):
        front, back = "", ""

        for field in card.find_all('rich-text'):
            text = field.decode_contents()
    
            for blob_id in re.findall(r"\{\{blob ([a-f0-9]+)\}\}", text):
                blob_filename = blob_map.get(blob_id, f"[missing {blob_id}]")
            
                if blob_filename.endswith((".jpg", ".png", ".gif", ".webp")):
                    text = text.replace(f"{{{{blob {blob_id}}}}}", f'<img src="{blob_filename}">')
                elif blob_filename.endswith(".mp3"):
                    text = text.replace(f"{{{{blob {blob_id}}}}}", f'<audio controls src="{blob_filename}"></audio>')
                else:
                    text = text.replace(f"{{{{blob {blob_id}}}}}", f"[missing or unknown blob: {blob_id}]")


            if field.get("name") == "front":
                front = clean_html(text).strip()
            elif field.get("name") == "back":
                back = clean_html(text).strip()

        if front and back:
            cards.append((front, back))
    
    return cards


def build_anki_package(cards, deck_name, media_files):
    model_id = random.randrange(1 << 30, 1 << 31)
    model = genanki.Model(
        model_id,
        "Front Back Model with Embeded Media",
        fields=[{"name" : "Question"}, {"name" : "Answer"}],
        templates=[
            {
                "name" : "Card 1",
                "qfmt" : "{{Question}}",
                "afmt": "{{FrontSide}}<hr id='answer'>{{Answer}}"
            }
        ],
        css="""
            .card {
                font-family: arial;
                font-size: 20px;
                text-align: center;
                color: black;
                background-color: white;
            }
        """
    )

    deck_id = random.randrange(1 << 30, 1 << 31)
    deck = genanki.Deck(deck_id, deck_name)

    for q, a in cards:
        deck.add_note(genanki.Note(model=model, fields=[q,a]))

    package = genanki.Package(deck)
    package.media_files = list(media_files)

    APKG_path = output_path / f"{deck_name}.apkg"
    package.write_to_file(APKG_path)

    print(f'Created APKG with path {APKG_path}. Delaying for two seconds and moving to next deck.')
    print('---------------------------------')

def convert(path):

    # Isolate blob path
    blob_path = Path(path) / 'blobs'

    # Isolate xml file and path
    xml_path = ''
    for f in Path.iterdir(path):
        if f.suffix == '.xml':
            xml_path = f

    # From XML path isolate filename removing white spaces
    deck_name = xml_path.stem.rstrip()

    print(f'\nStarting conversion on Deck {deck_name}. Isolating blobs if present.')

    # Need to first read all blobs in the respective folder and convert/map them
    blob_map, media_files = convert_blobs(blob_path, media_directory)

    print(f'Isolated {len(media_files)} blobs. Converted to correct file type.')
    print('Extracting cards from XML file for deck...')

    # Now extract all cards from Algo xml and replace bobs with appropriate anki html tag
    cards = read_algo(xml_path, blob_map)
    print(f'Extracted {len(cards)} cards from deck. Building Anki APKG for deck.')
    
    # Execute anki apkg maker
    build_anki_package(cards, deck_name, media_files)

    # Delay three seconds so can keep up with exeuction of code
    sleep(5)

def main():

    # Read each folder in Flashcard folder from Zahraa and start loop

    # Will read absolute path of current dir assuming algo decks here.
    # Absolute path to avoid any issues with relative path on windows
    algo_decks_path = Path(__file__).parent.absolute() / algo_decks_folder_name

    print(f'Assuming path of Algo Decks is located in {algo_decks_path}. Looping through folders...')

    # # Start loop
    for folder in Path.iterdir(algo_decks_path):
        if Path(folder).name == '.DS_Store':
            continue

        #Setup temp media file, clearing old file
        shutil.rmtree(media_directory, ignore_errors=True)
        os.makedirs(media_directory, exist_ok=True)

        #Run convert code with path
        convert(folder)

main()
