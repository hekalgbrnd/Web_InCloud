import streamlit as st
import os
import json
from pathlib import Path
import shutil
from streamlit_option_menu import option_menu
import requests

# Set Streamlit page configuration
st.set_page_config(page_title="In - Cloud", layout="wide", initial_sidebar_state="expanded")

# Load or initialize the favorite state
FAVORITES_FILE = "favorites.json"
if Path(FAVORITES_FILE).exists():
    with open(FAVORITES_FILE, "r") as f:
        favorites = json.load(f)
else:
    favorites = []

# Function to save the favorite state
def save_favorites(favorites):
    with open(FAVORITES_FILE, "w") as f:
        json.dump(favorites, f)

# Check if a folder is a favorite
def is_favorite(folder):
    return str(folder) in favorites

# Toggle favorite status of a folder
def toggle_favorite(folder):
    folder_str = str(folder)
    if folder_str in favorites:
        favorites.remove(folder_str)
    else:
        favorites.append(folder_str)
    save_favorites(favorites)

# Add custom CSS for styling
st.markdown("""
    <style>
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        margin: 5px;
        font-size: 16px;
    }
    .stTextInput>div>div>input {
        border: 2px solid #4CAF50;
        border-radius: 5px;
        padding: 10px;
    }
    .stFileUploader>div>div>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stDownloadButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
    }
    .stSelectbox>div>div>div>button {
        border: 2px solid #4CAF50;
        border-radius: 5px;
        padding: 10px;
        font-size: 16px;
    }
    .stCheckbox>div>div>input:checked + div > div {
        background-color: #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    selected = option_menu("InClouds", ["About Us", "Home", "Favorite"],
                           icons=["info", "house", "heart"], menu_icon="cast", default_index=1,
                           styles={"nav-link-selected": {"background-color": "#4CAF50"}})

# Configure main directory
BASE_DIR = Path("uploads")
if not BASE_DIR.exists():
    BASE_DIR.mkdir(parents=True, exist_ok=True)

# Function to create a folder if it does not exist
def buat_folder(path):
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)

# Function to add a document to a folder
def tambah_dokumen(folder, file):
    try:
        folder_path = BASE_DIR / folder
        buat_folder(folder_path)
        file_path = folder_path / file.name
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        st.success(f"File '{file.name}' berhasil diunggah ke folder '{folder}'.")
    except Exception as e:
        st.error(f"Gagal menambahkan dokumen: {e}")

# Function to rename a file
def ubah_nama_file(file_path, new_name):
    try:
        new_file_path = file_path.parent / new_name
        file_path.rename(new_file_path)
        st.success(f"File '{file_path.name}' berhasil diubah namanya menjadi '{new_name}'.")
    except Exception as e:
        st.error(f"Gagal mengubah nama file: {e}")

# Function to delete a file
def hapus_file(file_path):
    try:
        file_path.unlink()
        st.success(f"File '{file_path.name}' berhasil dihapus.")
    except Exception as e:
        st.error(f"Gagal menghapus file: {e}")

# Function to delete a folder
def hapus_folder(folder_path):
    try:
        shutil.rmtree(folder_path)
        st.success(f"Folder '{folder_path.name}' berhasil dihapus beserta isinya.")
    except Exception as e:
        st.error(f"Gagal menghapus folder: {e}")

# Function to rename a folder
def ubah_nama_folder(folder_path, new_name):
    try:
        new_folder_path = folder_path.parent / new_name
        folder_path.rename(new_folder_path)
        st.success(f"Folder '{folder_path.name}' berhasil diubah namanya menjadi '{new_name}'.")
    except Exception as e:
        st.error(f"Gagal mengubah nama folder: {e}")

# Function to calculate total storage size
def hitung_total_ukuran(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

# Placeholder function for Google Drive API implementation
def upload_to_google_drive(file_path, mime_type):
    # This is a placeholder function. Replace it with the actual Google Drive API implementation.
    # Here we are simulating that the file is uploaded to Google Drive and returning a dummy file ID.
    return f"dummy_google_file_id_{file_path.stem}"

# Function to display folder contents
def tampilkan_isi_folder(path, search_query=""):
    items = list(path.iterdir())
    files = [item for item in items if item.is_file() and search_query.lower() in item.name.lower()]
    folders = [item for item in items if item.is_dir() and search_query.lower() in item.name.lower()]

    st.write(f"Isi folder: {path.relative_to(BASE_DIR)}")
    if path != BASE_DIR and st.button("Kembali ke folder utama"):
        st.experimental_set_query_params(path="")

    st.write("### Folder")
    for folder in folders:
        col1, col2, col3, col4 = st.columns([5, 1, 1, 1])
        with col1:
            if st.button(f"📁 {folder.name}", key=f"folder_{folder.name}"):
                st.experimental_set_query_params(path=str(folder.relative_to(BASE_DIR)))
        with col2:
            if st.button("⚙️", key=f"settings_folder_{folder.name}"):
                menu_options = ["Rename", "Delete"]
                action = st.selectbox("", menu_options, key=f"menu_folder_{folder.name}")
                if action == "Rename":
                    new_name = st.text_input(f"Ubah nama folder '{folder.name}'", key=f"rename_folder_{folder.name}_input")
                    if st.button(f"Ubah Nama", key=f"btn_rename_folder_{folder.name}_confirm"):
                        if new_name:
                            ubah_nama_folder(folder, new_name)
                        else:
                            st.error("Nama folder baru tidak boleh kosong.")
                elif action == "Delete":
                    if st.button(f"Hapus Folder", key=f"btn_delete_folder_{folder.name}_confirm"):
                        hapus_folder(folder)
        with col3:
            is_fav = is_favorite(folder)
            if st.button("★" if is_fav else "☆", key=f"favorite_{folder.name}"):
                toggle_favorite(folder)
        with col4:
            st.write("")

    st.write("### File")
    for file in files:
        col1, col2, col3, col4 = st.columns([6, 1, 1, 1])
        with col1:
            file_name = file.name
            file_path = path / file_name
            mime_type = None
            google_url = None

            if file.suffix == ".docx":
                mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif file.suffix == ".xlsx":
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif file.suffix == ".pptx":
                mime_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            elif file.suffix == ".xls":
                mime_type = "application/vnd.ms-excel"
            elif file.suffix == ".doc":
                mime_type = "application/msword"
            elif file.suffix in [".png", ".jpg", ".jpeg", ".gif"]:
                if st.button(f"Open {file_name}", key=f"open_image_{file_name}"):
                    with open(file_path, "rb") as f:
                        image_bytes = f.read()
                    st.image(image_bytes, caption=file_name, use_column_width=True)
            elif file.suffix in [".mp4", ".mov", ".avi"]:
                if st.button(f"Play {file_name}", key=f"play_video_{file_name}"):
                    st.video(str(file_path))
            elif file.suffix in [".mp3", ".wav"]:
                if st.button(f"Play {file_name}", key=f"play_audio_{file_name}"):
                    st.audio(str(file_path))
            else:
                if st.button(f"{file_name}", key=f"file_{file_name}"):
                    google_url = f"https://drive.google.com/file/d/{upload_to_google_drive(file_path, mime_type)}/view"
                    if google_url:
                        st.write(f"File dapat diakses di Google Drive: [Open in Google Drive]({google_url})")

        with col2:
            menu_options = ["Rename", "Delete", "Download"]
            action = st.selectbox("", menu_options, key=f"menu_{file.name}")
            if action == "Rename":
                new_name = st.text_input(f"Ubah nama file '{file.name}'", key=f"rename_{file.name}_input")
                if st.button(f"Ubah Nama", key=f"btn_rename_{file.name}_confirm"):
                    if new_name:
                        ubah_nama_file(file, new_name)
                    else:
                        st.error("Nama file baru tidak boleh kosong.")
            elif action == "Delete":
                if st.button(f"Hapus File", key=f"btn_delete_{file.name}_confirm"):
                    hapus_file(file)
            elif action == "Download":
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="Download",
                        data=f,
                        file_name=file.name,
                        mime="application/octet-stream",
                        key=f"download_{file.name}"
                    )
        with col3:
            st.write("")
        with col4:
            st.write("")

# Streamlit Application
st.markdown("<h1 style='text-align: center; color: #4CAF50; font-family: 'Arial', sans-serif; font-size: 50px;'>InClouds</h1>", unsafe_allow_html=True)

#logo_path = "asset/logo.png"
#st.sidebar.image(logo_path)

if selected == "Home":
    # Read query parameter for folder navigation
    query_params = st.experimental_get_query_params()
    current_path_str = query_params.get("path", [""])[0]
    current_path = BASE_DIR / current_path_str

    # Display total storage size
    total_storage_used = hitung_total_ukuran(BASE_DIR)
    st.write(f"Total penyimpanan yang terpakai: {total_storage_used / (1024 * 1024):.2f} MB")

    # Create a new folder
    st.header("Buat Folder")
    folder_name = st.text_input("Nama Folder")
    if st.button("Buat Folder"):
        if folder_name:
            buat_folder(current_path / folder_name)
            st.success(f"Folder '{folder_name}' berhasil dibuat.")
        else:
            st.error("Nama folder tidak boleh kosong")

    # Upload a new file
    st.header("Unggah File")
    uploaded_file = st.file_uploader("Pilih File")
    if uploaded_file and st.button("Unggah File"):
        if uploaded_file.size <= 1 * 1024 * 1024 * 1024:  # Check if file size is less than or equal to 1GB
            tambah_dokumen(current_path_str, uploaded_file)
        else:
            st.error("Ukuran file tidak boleh lebih dari 1GB")

    # Search bar for searching files and folders
    st.header("Pencarian")
    search_query = st.text_input("Cari folder atau file")

    # Display current folder contents with search query
    tampilkan_isi_folder(current_path, search_query)

elif selected == "Settings":
    st.write("Settings page content can go here.")

elif selected == "About Us":
    st.markdown("<h1 style='text-align: center; color: #4CAF50; font-family: 'Arial', sans-serif; font-size: 30px;'>About Us</h1>", unsafe_allow_html=True)
    st.write("""
    Welcome to the About Us page!

    This Streamlit app is developed by YARSI Information Technology Faculty Cloud Computing team.
    """)

elif selected == "Favorite":
    st.title("Favorite Folders")
   
    favorite_folders = [Path(folder) for folder in favorites if Path(folder).is_dir()]
    for folder in favorite_folders:
        if st.button(f"📁 {folder.name}", key=f"favorite_folder_{folder.name}"):
            st.experimental_set_query_params(path=str(folder.relative_to(BASE_DIR)))
