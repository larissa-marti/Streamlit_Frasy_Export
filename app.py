import streamlit as st
import pandas as pd
import zipfile
import os
from io import BytesIO

# Startpositionen der Spalten
start_positionen = [0, 3, 8, 16, 21, 23, 24, 28, 32, 36, 40, 44, 48, 52, 56, 59, 62]

# Spaltenbreiten berechnen
spaltenbreiten = [j - i for i, j in zip(start_positionen[:-1], start_positionen[1:])]
# Füge eine Spalte hinzu, die bis zum Ende der Zeile reicht (max. 20 Zeichen → reicht für Didok-Code aber völlig)
spaltenbreiten.append(20)

# Funktion zum Einlesen der Textdatei in einem DataFrame
def lese_textdatei_als_df(zip_pfad, dateiname):
    with zipfile.ZipFile(zip_pfad, 'r') as zip_ref:
        with zip_ref.open(dateiname) as file:
            # Textdatei in DataFrame einlesen
            df = pd.read_fwf(file, widths=spaltenbreiten, header=None, dtype=str)
            return df


st.title("Frasy-Export-Verarbeitungstool")


uploaded_file = st.file_uploader("Lade eine .zip oder .txt Datei hoch", type=["zip", "txt"])

if uploaded_file:
    if uploaded_file.name.endswith(".zip"):
        with zipfile.ZipFile(uploaded_file, 'r') as zip_ref:
            dateinamen = zip_ref.namelist()
            if len(dateinamen) == 1 and dateinamen[0].endswith('.txt'):
                dateiname = dateinamen[0]
                df = lese_textdatei_als_df(uploaded_file, dateiname)
    elif uploaded_file.name.endswith(".txt"):
        df = pd.read_fwf(uploaded_file, widths=spaltenbreiten, header=None, dtype=str)

    # 6-stellige Zugnummer sicherstellen
    df[1] = df[1].apply(lambda x: '0' + x.zfill(5))

    # DataFrame als Textdatei im Speicher speichern
    txt_buffer = BytesIO()
    df.to_csv(txt_buffer, index=False, header=False, sep=';')
    txt_buffer.seek(0)

    # Originaldateiname ohne Endung
    base_filename = os.path.splitext(uploaded_file.name)[0]

    # Textdatei in ein ZIP-Archiv im Speicher komprimieren
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr(base_filename + '_processed.txt', txt_buffer.getvalue())
    zip_buffer.seek(0)

    st.success("Die Datei wurde erfolgreich verarbeitet!")

    st.download_button("Download verarbeitete .txt Datei", data=txt_buffer, file_name=base_filename + '_processed.txt')
    st.download_button("Download verarbeitete .zip Datei", data=zip_buffer, file_name=base_filename + '_processed.zip')
