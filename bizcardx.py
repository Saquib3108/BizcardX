# -*- coding: utf-8 -*-
"""BizCardX.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1MpttQhPZAzZwnomFtx66f2XvV5qO73uU
"""

! pip install easyocr

! pip install streamlit

! pip install streamlit_option_menu

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

  #converting image to array format

  img_arr = np.array(input_img)

  reader = easyocr.Reader(['en'])
  img_arr = np.array(input_img)
  text = reader.readtext(img_arr, detail = 0)

  return text, input_img

text_img, input_img = image_to_text("/content/1.png")

text_img, input_img = image_to_text("/content/2.png")

text_img, input_img = image_to_text("/content/3.png")

text_img, input_img = image_to_text("/content/4.png")

text_img, input_img = image_to_text("/content/5.png")

from typing import Concatenate
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

    elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i]:
      small = texts[i].lower()
      extrctd_dict["WEBSITE"].append(small)

    elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i]  or texts[i].isdigit():
      extrctd_dict["PINCODE"].append(texts[i])

    elif re.match(r'^[A-Za-z]', texts[i]):
      extrctd_dict["COMPANY_NAME"].append(texts[i])

    else:
      remove_colon = re.sub(r'[,;]','', texts[i])
      extrctd_dict["ADDRESS"].append(remove_colon)

  for key, value in extrctd_dict.items():

    if len(value)>0:
      Concatenate = " ".join(value)
      extrctd_dict[key] = [Concatenate]

    else:
      value = "NA"
      extrctd_dict[key] = [value]

  return extrctd_dict

text_data = extracted_text(text_img)

df = pd.DataFrame(text_data)
df

text_img

input_img

#converting image to bytes

Image_bytes = io.BytesIO()
input_img.save(Image_bytes, format = "PNG")

image_data = Image_bytes.getvalue()

#creating dictionary

data= {"IMAGE":[image_data]}
df_1 = pd.DataFrame(data)

concat_df = pd.concat([df,df_1],axis= 1)

concat_df

mydb = sqlite3.connect("bizCard.db")
cursor = mydb.cursor()

#Table creation

create_table_query = ''' CREATE TABLE IF NOT EXISTS bizcardX_db(name varchar(255),
                                                                designation varchar(255),
                                                                company_name varchar(200),
                                                                contact varchar(225),
                                                                email varchar(225),
                                                                website text,
                                                                address text,
                                                                pincode varchar(225),
                                                                image text)'''

cursor.execute(create_table_query)
mydb.commit()

#Insert query

insert_query = '''INSERT INTO bizcardX_db(name, designation, company_name,contact, email, website, address,
                                                    pincode, image)

                                                    values(?,?,?,?,?,?,?,?,?)'''

datas = concat_df.values.tolist()[0]
cursor.execute(insert_query,datas)
mydb.commit()

# Commented out IPython magic to ensure Python compatibility.
# %%writefile bixCard_app.py
# 
# 
# import streamlit as st
# from streamlit_option_menu import option_menu
# import easyocr
# from PIL import Image
# import pandas as pd
# import numpy as np
# import re
# from typing import Concatenate
# import io
# import sqlite3
# 
# 
# def image_to_text(path):
# 
#   input_img = Image.open(path)
# 
#   #converting image to array format
# 
#   img_arr = np.array(input_img)
# 
#   reader = easyocr.Reader(['en'])
#   img_arr = np.array(input_img)
#   text = reader.readtext(img_arr, detail = 0)
# 
#   return text, input_img
# 
# 
# def extracted_text(texts):
# 
#     extrctd_dict = {"NAME":[], "DESIGNATION": [], "COMPANY_NAME":[], "CONTACT":[], "EMAIL":[],
#                   "WEBSITE":[], "ADDRESS":[], "PINCODE":[]}
# 
#     extrctd_dict["NAME"].append(texts[0])
#     extrctd_dict["DESIGNATION"].append(texts[1])
# 
#     for i in range(2, len(texts)):
# 
#       if texts[i].startswith("+") or (texts[i].replace("-","").isdigit() and '-' in texts[i]):
#         extrctd_dict["CONTACT"].append(texts[i])
# 
#       elif "@" in texts[i] and ".com" in texts[i]:
#         extrctd_dict["EMAIL"].append(texts[i])
# 
#       elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i]:
#         small = texts[i].lower()
#         extrctd_dict["WEBSITE"].append(small)
# 
#       elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i]  or texts[i].isdigit():
#         extrctd_dict["PINCODE"].append(texts[i])
# 
#       elif re.match(r'^[A-Za-z]', texts[i]):
#         extrctd_dict["COMPANY_NAME"].append(texts[i])
# 
#       else:
#         remove_colon = re.sub(r'[,;]','', texts[i])
#         extrctd_dict["ADDRESS"].append(remove_colon)
# 
#     for key, value in extrctd_dict.items():
# 
#       if len(value)>0:
#         Concatenate = " ".join(value)
#         extrctd_dict[key] = [Concatenate]
# 
#       else:
#         value = "NA"
#         extrctd_dict[key] = [value]
# 
#     return extrctd_dict
# 
# 
# #streamlit
# 
# st.set_page_config(layout= "wide")
# st.title("EXTRACTING BUSINESS CARD WITH 'OCR'")
# 
# with st.sidebar:
# 
#   select = option_menu("Main Menu", ["Home", "Upload & Modifying", "Delete"])
# 
# if select == "Home":
#   pass
# 
# elif select == "Upload & Modifying":
#   img = st.file_uploader("Upload the Image", type= ["png","jpg","jpeg"])
# 
#   if img is not None:
#     st.image(img, width= 300)
# 
#     text_image, input_img= image_to_text(img)
# 
#     text_dict = extracted_text(text_image)
# 
#     if text_dict:
#       st.success("TEXT IS EXTRACTED SUCCESSFULLY")
# 
#     df= pd.DataFrame(text_dict)
# 
#     #converting image to bytes
# 
#     Image_bytes = io.BytesIO()
#     input_img.save(Image_bytes, format = "PNG")
# 
#     image_data = Image_bytes.getvalue()
# 
#     #creating dictionary
# 
#     data= {"IMAGE":[image_data]}
#     df_1 = pd.DataFrame(data)
# 
#     concat_df = pd.concat([df,df_1],axis= 1)
# 
#     st.dataframe(concat_df)
# 
#     button_1 = st.button("Save")
# 
#     if button_1:
# 
#       mydb = sqlite3.connect("bizCard.db")
#       cursor = mydb.cursor()
# 
#       #Table creation
# 
#       create_table_query = ''' CREATE TABLE IF NOT EXISTS bizcardX_db(name varchar(255),
#                                                                 designation varchar(255),
#                                                                 company_name varchar(200),
#                                                                 contact varchar(225),
#                                                                 email varchar(225),
#                                                                 website text,
#                                                                 address text,
#                                                                 pincode varchar(225),
#                                                                 image text)'''
# 
#       cursor.execute(create_table_query)
#       mydb.commit()
# 
#       #Insert query
# 
#       insert_query = '''INSERT INTO bizcardX_db(name, designation, company_name,contact, email, website, address,
#                                                     pincode, image)
# 
#                                                     values(?,?,?,?,?,?,?,?,?)'''
# 
#       datas = concat_df.values.tolist()[0]
#       cursor.execute(insert_query,datas)
#       mydb.commit()
# 
#       st.success("SAVED SUCCESSFULLY")
# 
#   method =  st.radio("Select the Method",["None","Preview","Modify"])
# 
#   if method == "None":
#     st.write("")
# 
#   if method == "Preview":
#     mydb = sqlite3.connect("bizCard.db")
#     cursor = mydb.cursor()
# 
#     select_query = "SELECT * FROM bizcardX_db"
# 
#     cursor.execute(select_query)
#     table = cursor.fetchall()
#     mydb.commit()
# 
#     table_df = pd.DataFrame(table, columns=("NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE",
#                                                 "ADDRESS", "PINCODE", "IMAGE"))
#     st.dataframe(table_df)
# 
#   elif method == "Modify":
#     mydb = sqlite3.connect("bizCard.db")
#     cursor = mydb.cursor()
# 
#     select_query = "SELECT * FROM bizcardX_db"
# 
#     cursor.execute(select_query)
#     table = cursor.fetchall()
#     mydb.commit()
# 
#     table_df = pd.DataFrame(table, columns=("NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE",
#                                                 "ADDRESS", "PINCODE", "IMAGE"))
# 
#     col1,col2 = st.columns(2)
#     with col1:
# 
#       selected_name = st.selectbox("Select the name", table_df["NAME"])
# 
#     df_3 = table_df[table_df["NAME"] == selected_name]
# 
#     df_4 = df_3.copy()
# 
#     col1,col2 = st.columns(2)
#     with col1:
#       mo_name = st.text_input("Name", df_3["NAME"].unique()[0])
#       mo_desi = st.text_input("Designation", df_3["DESIGNATION"].unique()[0])
#       mo_com_name = st.text_input("Company_name", df_3["COMPANY_NAME"].unique()[0])
#       mo_contact = st.text_input("Contact", df_3["CONTACT"].unique()[0])
#       mo_email = st.text_input("Email", df_3["EMAIL"].unique()[0])
# 
#       df_4["NAME"] = mo_name
#       df_4["DESIGNATION"] = mo_desi
#       df_4["COMPANY_NAME"] = mo_com_name
#       df_4["CONTACT"] = mo_contact
#       df_4["EMAIL"] = mo_email
# 
#     with col2:
# 
#       mo_website = st.text_input("Website", df_3["WEBSITE"].unique()[0])
#       mo_addre = st.text_input("Address", df_3["ADDRESS"].unique()[0])
#       mo_pincode = st.text_input("Pincode", df_3["PINCODE"].unique()[0])
#       mo_image = st.text_input("Image", df_3["IMAGE"].unique()[0])
# 
#       df_4["WEBSITE"] = mo_website
#       df_4["ADDRESS"] = mo_addre
#       df_4["PINCODE"] = mo_pincode
#       df_4["IMAGE"] = mo_image
# 
#     st.dataframe(df_4)
# 
#     col1,col2= st.columns(2)
#     with col1:
#       button_3 = st.button("Modify", use_container_width = True)
# 
#     if button_3:
#       mydb = sqlite3.connect("bizCard.db")
#       cursor = mydb.cursor()
# 
#       cursor.execute(f"DELETE FROM bizcardX_db WHERE NAME = '{selected_name}'")
#       mydb.commit()
# 
#       #Insert query
# 
#       insert_query = '''INSERT INTO bizcardX_db(name, designation, company_name,contact, email, website, address,
#                                                     pincode, image)
# 
#                                                     values(?,?,?,?,?,?,?,?,?)'''
# 
#       datas = df_4.values.tolist()[0]
#       cursor.execute(insert_query,datas)
#       mydb.commit()
# 
#       st.success("MODIFIED SUCCESSFULLY")
# 
# elif select == "Delete":
#   pass
#

!wget -q -O - ipv4.icanhazip.com

! streamlit run bixCard_app.py & npx localtunnel --port 8501