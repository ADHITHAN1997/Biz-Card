#import packages
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import sqlite3

#check image details
check_image= Image.open(r"C:\Users\study\Downloads\vs code\1.png")
#check_image

 # converting image to text formet
def image_to_text(image_path):
  input_image= Image.open(image_path)
  image_arr= np.array(input_image)

  reader= easyocr.Reader(['en'])
  text= reader.readtext(image_arr,detail= 0)

  return text,input_image

text_data=image_to_text(r"C:\Users\study\Downloads\vs code\1.png")

def data_extract(text_details):
    text_dict = {
        "NAME": [text_details[0]],
        "DESIGNATION": [text_details[1]],
        "COMPANY_NAME": [],
        "CONTACT": [],
        "EMAIL": [],
        "WEBSITE": [],
        "ADDRESS": [],
        "PINCODE": []
    }

    for text in text_details[2:]:
        if text.startswith("+") or (text.replace("-", "").isdigit() and "-" in text):
            text_dict["CONTACT"].append(text)
        elif "@" in text and ".com" in text:
            text_dict["EMAIL"].append(text)
        elif "www" in text.lower():
            text_dict["WEBSITE"].append(text.lower())
        elif any(x in text.lower() for x in ["tamil nadu", "tamilnadu"]) or text.isdigit():
            text_dict["PINCODE"].append(text)
        elif re.match(r'^[A-Za-z]', text):
            text_dict["COMPANY_NAME"].append(text)
        else:
            text_dict["ADDRESS"].append(re.sub(r'[,;]', '', text))
    # handle empty lists
    for key, value in text_dict.items():
      if value:
          text_dict[key] = [', '.join(value)]
      else:
          text_dict[key] = ["NA"]

    return text_dict

#Streamlit part
st.set_page_config(layout = "wide")
st.title("EXTRACTING BUSINESS CARD DATA WITH OCR")

with st.sidebar:

  select= option_menu("Main Menu", ["Home", "Upload & Modifying", "Delete"])

if select == "Home":
  st.markdown("### :blue[**Technologies Used :**] Python,easy OCR, Streamlit, SQL, Pandas")

  st.write(
            "### :red[**About :**] Bizcard is a Python application designed to extract information from business cards.")
  st.write(
            '### The main purpose of Bizcard is to automate the process of extracting key details from business card images, such as the name, designation, company, contact information, and other relevant data.OCR (Optical Character Recognition) provided by EasyOCR, Bizcard is able to extract text from the images.')

elif select == "Upload & Modifying":
  img = st.file_uploader("Upload the Image", type= ["png","jpg","jpeg"])

  if img is not None:
    st.image(img, width= 400)
    extract_image,input_image = image_to_text(img)

    text_dict= data_extract(extract_image)
  
    if text_dict:
        st.success("TEXT IS EXTRACTED SUCCESSFULLY")
    st.write("Extracted Data")
    df= pd.DataFrame(text_dict)
    
    #Converting Image to Bytes
    Image_bytes = io.BytesIO()
    input_image.save(Image_bytes, format= "PNG")

    image_data = Image_bytes.getvalue()

    #Creating bytes dataframe
    data = {"IMAGE":[image_data]}

    df1 = pd.DataFrame(data)

    #concatenate two dataframe
    concat_df = pd.concat([df,df1],axis= 1)
    st.dataframe(concat_df)

    button_1 = st.button("Save")

    if button_1:
      connection = sqlite3.connect("bizcardx.db")
      cursor = connection.cursor()

      #Table Creation
      create_table_query = '''CREATE TABLE IF NOT EXISTS bizcard_details(name varchar(225),
                                                                          designation varchar(225),
                                                                          company_name varchar(225),
                                                                          contact varchar(225),
                                                                          email varchar(225),
                                                                          website text,
                                                                          address text,
                                                                          pincode varchar(225),
                                                                          image text)'''

      cursor.execute(create_table_query)
      connection.commit()

      #Insert Query
      insert_query = '''INSERT INTO bizcard_details(name, designation, company_name,contact, email, website, address,
                                                    pincode, image)
                                                    values(?,?,?,?,?,?,?,?,?)'''

      datas = concat_df.values.tolist()[0]
      cursor.execute(insert_query,datas)
      connection.commit()
      st.success("SAVED SUCCESSFULLY")
    
  method =  st.radio("Select the Method",["None","Preview","Modify"])

  if method == "None":
        st.write("")
  if method == "Preview":
        connection = sqlite3.connect("bizcardx.db")
        cursor = connection.cursor()

        #select query
        select_query = "SELECT * FROM bizcard_details"

        cursor.execute(select_query)
        table = cursor.fetchall()
        connection.commit()

        table_df = pd.DataFrame(table, columns=("NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE",
                                                "ADDRESS", "PINCODE", "IMAGE"))
        st.dataframe(table_df)

  elif method == "Modify":
        connection = sqlite3.connect("bizcardx.db")
        cursor = connection.cursor()

        #select query
        select_query = "SELECT * FROM bizcard_details"

        cursor.execute(select_query)
        table = cursor.fetchall()
        connection.commit()

        table_df = pd.DataFrame(table, columns=("NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE",
                                                "ADDRESS", "PINCODE", "IMAGE"))
        
        col1,col2 = st.columns(2)
        with col1:
            select_name = st.selectbox("Select the name", table_df["NAME"])

        df1 = table_df[table_df["NAME"] == select_name]
        df2 = df1.copy() 

        col1,col2 = st.columns(2)
        with col1:
            modify_name = st.text_input("Name", df1["NAME"].unique()[0])
            modify_designation = st.text_input("Designation", df1["DESIGNATION"].unique()[0])
            modify_company_name = st.text_input("Company_name", df1["COMPANY_NAME"].unique()[0])
            modify_contact = st.text_input("Contact", df1["CONTACT"].unique()[0])
            modify_email = st.text_input("Email", df1["EMAIL"].unique()[0])

            df2["NAME"] = modify_name
            df2["DESIGNATION"] = modify_designation
            df2["COMPANY_NAME"] = modify_company_name
            df2["CONTACT"] = modify_contact
            df2["EMAIL"] = modify_email
        
        with col2:
            modify_website = st.text_input("Website", df1["WEBSITE"].unique()[0])
            modify_address = st.text_input("Address", df1["ADDRESS"].unique()[0])
            modify_pincode = st.text_input("Pincode", df1["PINCODE"].unique()[0])
            modify_image = st.text_input("Image", df1["IMAGE"].unique()[0])

            df2["WEBSITE"] = modify_website
            df2["ADDRESS"] = modify_address
            df2["PINCODE"] = modify_pincode
            df2["IMAGE"] = modify_image

        st.write("Modified Data")
        st.dataframe(df2)


        col1,col2= st.columns(2)
        with col1:
           button_3 = st.button("Modify Data Saved")

        if button_3:
           connection = sqlite3.connect("bizcardx.db")
           cursor = connection.cursor()

           cursor.execute(f"DELETE FROM bizcard_details WHERE NAME = '{select_name}'")
           connection.commit()

           # modified Insert Query
           insert_query = '''INSERT INTO bizcard_details(name, designation, company_name,contact, email, website, address,
                                                            pincode, image)

                                                            values(?,?,?,?,?,?,?,?,?)'''

           datas = df2.values.tolist()[0]
           cursor.execute(insert_query,datas)
           connection.commit()

           st.success("MODIFIED DATA SAVED SUCCESSFULLY")

elif select == "Delete":
    connection = sqlite3.connect("bizcardx.db")
    cursor = connection.cursor()

    col1,col2 = st.columns(2)
    with col1:
        select_query = "SELECT NAME FROM bizcard_details"

        cursor.execute(select_query)
        table1 = cursor.fetchall()
        connection.commit()

        names = []

        for i in table1:
            names.append(i[0])
        
        name_select = st.selectbox("Select the name", names)

    with col2:
        select_query = f"SELECT DESIGNATION FROM bizcard_details WHERE NAME ='{name_select}'"

        cursor.execute(select_query)
        table2 = cursor.fetchall()
        connection.commit()

        designations = []

        for j in table2:
            designations.append(j[0])

        designation_select = st.selectbox("Select the designation", options = designations)

    if name_select and designation_select:

        col1,col2,col3 = st.columns(3)
        with col1:
            st.write(f"Selected Name : {name_select}")
         
            st.write(f"Selected Designation : {designation_select}")
           
            remove = st.button("Delete")

            if remove:
                cursor.execute(f"DELETE FROM bizcard_details WHERE NAME ='{name_select}' AND DESIGNATION = '{designation_select}'")
                connection.commit()

                st.warning(f"{name_select.upper()} DATA DELETED")

