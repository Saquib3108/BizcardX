import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import sqlite3

def image_to_text(path):
    input_img = Image.open(path)
    img_arr = np.array(input_img)
    reader = easyocr.Reader(['en'])
    text = reader.readtext(img_arr, detail=0)
    return text, input_img

def extracted_text(texts):
    extrctd_dict = {"NAME":[], "DESIGNATION": [], "COMPANY_NAME":[], "CONTACT":[], "EMAIL":[],
                    "WEBSITE":[], "ADDRESS":[], "PINCODE":[]}

    extrctd_dict["NAME"].append(texts[0])
    extrctd_dict["DESIGNATION"].append(texts[1])

    for i in range(2, len(texts)):
        if texts[i].startswith("+") or (texts[i].replace("-","").isdigit() and '-' in texts[i]):
            extrctd_dict["CONTACT"].append(texts[i])
        elif "@" in texts[i] and ".com" in texts[i]:
            extrctd_dict["EMAIL"].append(texts[i])
        elif any(sub in texts[i].lower() for sub in ["www", "http"]):
            extrctd_dict["WEBSITE"].append(texts[i].lower())
        elif re.match(r'^\d{5,6}$', texts[i]):
            extrctd_dict["PINCODE"].append(texts[i])
        elif re.match(r'^[A-Za-z]', texts[i]):
            extrctd_dict["COMPANY_NAME"].append(texts[i])
        else:
            extrctd_dict["ADDRESS"].append(re.sub(r'[,;]','', texts[i]))

    for key, value in extrctd_dict.items():
        extrctd_dict[key] = [" ".join(value) if value else "NA"]

    return extrctd_dict

# Database functions
def create_connection():
    conn = sqlite3.connect('bizCard.db')
    return conn

def create_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(''' CREATE TABLE IF NOT EXISTS bizcardX_db(
                        name TEXT,
                        designation TEXT,
                        company_name TEXT,
                        contact TEXT,
                        email TEXT,
                        website TEXT,
                        address TEXT,
                        pincode TEXT,
                        image BLOB,
                        UNIQUE(name, designation, company_name)) ''')
    conn.commit()
    conn.close()

def save_to_database(data):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM bizcardX_db WHERE name = ? AND designation = ? AND company_name = ?''', 
                   (data[0], data[1], data[2]))
    result = cursor.fetchone()
    if result:
        conn.close()
        return False
    else:
        cursor.execute('''INSERT INTO bizcardX_db (name, designation, company_name, contact, email, website, address, pincode, image)
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
        conn.commit()
        conn.close()
        return True

def get_all_records():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bizcardX_db")
    records = cursor.fetchall()
    conn.close()
    return records

def delete_record(name, designation):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bizcardX_db WHERE name = ? AND designation = ?", (name, designation))
    conn.commit()
    conn.close()

# Streamlit UI
st.set_page_config(layout="wide")
st.title("EXTRACTING BUSINESS CARD DATA WITH 'OCR'")

with st.sidebar:
    select = option_menu("Main Menu", ["Home", "Upload & Modifying", "Delete"])

create_table()

if select == "Home":
    st.markdown("### :blue[**Technologies Used :**] Python, EasyOCR, Streamlit, SQLite, Pandas")
    st.write(
        "### :green[**About :**] Bizcard is a Python application designed to extract information from business cards.")
    st.write(
        '### The main purpose of Bizcard is to automate the process of extracting key details from business card images, such as the name, designation, company, contact information, and other relevant data. By leveraging the power of OCR (Optical Character Recognition) provided by EasyOCR, Bizcard is able to extract text from the images.')

elif select == "Upload & Modifying":
    img = st.file_uploader("Upload the Image", type=["png", "jpg", "jpeg"])

    if img is not None:
        st.image(img, width=300)
        text_image, input_img = image_to_text(img)
        text_dict = extracted_text(text_image)

        if text_dict:
            st.success("TEXT IS EXTRACTED SUCCESSFULLY")

        df = pd.DataFrame(text_dict)

        Image_bytes = io.BytesIO()
        input_img.save(Image_bytes, format="PNG")
        image_data = Image_bytes.getvalue()
        df['IMAGE'] = [image_data]

        st.dataframe(df)

        if st.button("Save"):
            data = df.values.tolist()[0]
            if save_to_database(data):
                st.success("SAVED SUCCESSFULLY")
            else:
                st.warning("DUPLICATE DATA - ALREADY EXISTS IN DATABASE")

    method = st.radio("Select the Method", ["None", "Preview", "Modify"])

    if method == "Preview":
        records = get_all_records()
        if records:
            table_df = pd.DataFrame(records, columns=["NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE", "ADDRESS", "PINCODE", "IMAGE"])
            st.dataframe(table_df)

    elif method == "Modify":
        records = get_all_records()
        if records:
            table_df = pd.DataFrame(records, columns=["NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE", "ADDRESS", "PINCODE", "IMAGE"])
            col1, col2 = st.columns(2)
            with col1:
                selected_name = st.selectbox("Select the name", table_df["NAME"])

            df_3 = table_df[table_df["NAME"] == selected_name]

            if not df_3.empty:
                df_4 = df_3.copy()
                col1, col2 = st.columns(2)
                with col1:
                    mo_name = st.text_input("Name", df_3["NAME"].values[0])
                    mo_desi = st.text_input("Designation", df_3["DESIGNATION"].values[0])
                    mo_com_name = st.text_input("Company_name", df_3["COMPANY_NAME"].values[0])
                    mo_contact = st.text_input("Contact", df_3["CONTACT"].values[0])
                    mo_email = st.text_input("Email", df_3["EMAIL"].values[0])

                    df_4["NAME"] = mo_name
                    df_4["DESIGNATION"] = mo_desi
                    df_4["COMPANY_NAME"] = mo_com_name
                    df_4["CONTACT"] = mo_contact
                    df_4["EMAIL"] = mo_email

                with col2:
                    mo_website = st.text_input("Website", df_3["WEBSITE"].values[0])
                    mo_address = st.text_input("Address", df_3["ADDRESS"].values[0])
                    mo_pincode = st.text_input("Pincode", df_3["PINCODE"].values[0])
                    mo_image = df_3["IMAGE"].values[0]

                    df_4["WEBSITE"] = mo_website
                    df_4["ADDRESS"] = mo_address
                    df_4["PINCODE"] = mo_pincode
                    df_4["IMAGE"] = mo_image

                st.dataframe(df_4)

                if st.button("Modify"):
                    delete_record(selected_name, df_3["DESIGNATION"].values[0])
                    data = df_4.values.tolist()[0]
                    if save_to_database(data):
                        st.success("MODIFIED SUCCESSFULLY")

elif select == "Delete":
    records = get_all_records()
    if records:
        table_df = pd.DataFrame(records, columns=["NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE", "ADDRESS", "PINCODE", "IMAGE"])
        col1, col2 = st.columns(2)
        with col1:
            name_select = st.selectbox("Select the name", table_df["NAME"])

        df_3 = table_df[table_df["NAME"] == name_select]

        if not df_3.empty:
            designation_select = df_3["DESIGNATION"].values[0]
            with col2:
                st.write(f"Selected Name: {name_select}")
                st.write(f"Selected Designation: {designation_select}")

                if st.button("Delete", use_container_width=True):
                    delete_record(name_select, designation_select)
                    st.success("DELETED SUCCESSFULLY")