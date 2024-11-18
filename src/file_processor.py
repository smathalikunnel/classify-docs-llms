import os
import logging
import mimetypes
from pdf2image import convert_from_path  # Needs poppler (installation via Homebrew in macOS environments)
from dotenv import load_dotenv
import docx2pdf  # Convert Word to PDF
import pandas as pd


# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FileProcessor:
    def __init__(self, output_folder="data/images"):
        self.output_folder = output_folder
        # Ensure output folder exists
        os.makedirs(self.output_folder, exist_ok=True)

    def process_file(self, file_path):
        """
        Process the given file by determining its type and converting it accordingly.

        Args:
            file_path (str): The path to the file to be processed.

        Returns:
            str: Path to the processed image.

        Raises:
            ValueError: If the file type is not supported.
        """
        file_type, _ = mimetypes.guess_type(file_path)
        
        if file_type == "application/pdf":
            return self.convert_pdf_to_images(file_path)
        elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            pdf_path = self.convert_word_to_pdf(file_path)
            return self.convert_pdf_to_images(pdf_path)
        elif file_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
            pdf_path = self.convert_excel_to_pdf(file_path)
            return self.convert_pdf_to_images(pdf_path)
        elif file_type == "image/jpeg" or file_type == "image/png":
            # Directly return the image path for jpg/png files
            return file_path
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

    def convert_pdf_to_images(self, pdf_path):
        """
        Convert a PDF file to images. Only the first page is saved as an image.

        Args:
            pdf_path (str): The path to the PDF file to be converted.

        Returns:
            str: Path to the saved image.
        """
        try:
            images = convert_from_path(pdf_path)
            output_filename = os.path.splitext(os.path.basename(pdf_path))[0] + "_page_1.png"
            output_path = os.path.join(self.output_folder, output_filename)
            images[0].save(output_path, "PNG")
            logger.info(f"Saved image to {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Error converting PDF to images: {e}")
            raise

    def convert_word_to_pdf(self, word_path):
        """
        Convert a Word document to PDF.

        Args:
            word_path (str): The path to the Word file to be converted.

        Returns:
            str: Path to the converted PDF.
        """
        try:
            pdf_path = word_path.replace(".docx", ".pdf")
            docx2pdf.convert(word_path, pdf_path)
            logger.info(f"Converted Word document to PDF: {pdf_path}")
            return pdf_path
        except Exception as e:
            logger.error(f"Error converting Word to PDF: {e}")
            raise

    def convert_excel_to_pdf(self, excel_path):
        """
        Convert an Excel document to PDF.

        Args:
            excel_path (str): The path to the Excel file to be converted.

        Returns:
            str: Path to the converted PDF.
        """
        try:
            excel_data = pd.read_excel(excel_path, sheet_name=None)
            pdf_path = excel_path.replace(".xlsx", ".pdf")
            with pd.ExcelWriter(pdf_path, engine='xlsxwriter') as writer:
                for sheet_name, df in excel_data.items():
                    df.to_excel(writer, sheet_name=sheet_name)
            logger.info(f"Converted Excel document to PDF: {pdf_path}")
            return pdf_path
        except Exception as e:
            logger.error(f"Error converting Excel to PDF: {e}")
            raise
