import streamlit as st
import pytesseract
from PIL import Image
import pandas as pd
import fitz  # PyMuPDF

# Set the path for Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # Update this path if necessary

def extract_text_from_image(image):
    return pytesseract.image_to_string(image)

def extract_images_from_pdf(uploaded_file):
    pdf = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    images = []
    for page_num in range(len(pdf)):
        page = pdf.load_page(page_num)
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images

# Streamlit UI
st.title("Invoice OCR Web App")
st.write("Upload an invoice image or PDF to extract information and save it to a CSV file.")

uploaded_file = st.file_uploader("Choose an image or PDF...", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file is not None:
    file_type = uploaded_file.type
    extracted_text = ""

    if file_type == "application/pdf":
        images = extract_images_from_pdf(uploaded_file)
        for img in images:
            extracted_text += extract_text_from_image(img) + "\n"
        st.image(images, caption='Uploaded PDF as Images', use_column_width=True)
    else:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
        extracted_text = extract_text_from_image(image)
    
    st.write("")
    st.write("Extracted Text:")
    st.write(extracted_text)

    # Processing the text to extract relevant invoice information
    invoice_data = {
        "Date": [],
        "Invoice Number": [],
        "Total Amount": []
    }
    
    for line in extracted_text.split('\n'):
        if "Date" in line:
            invoice_data["Date"].append(line.split(":")[-1].strip())
        elif "Invoice Number" in line:
            invoice_data["Invoice Number"].append(line.split(":")[-1].strip())
        elif "Total" in line:
            invoice_data["Total Amount"].append(line.split(":")[-1].strip())
    
    # Convert to DataFrame
    df = pd.DataFrame(invoice_data)
    
    # Display DataFrame
    st.write(df)

    # Save to CSV
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='invoice_data.csv',
        mime='text/csv',
    )
