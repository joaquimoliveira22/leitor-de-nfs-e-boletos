import os
import PyPDF2
import re

def extract_all_cnpjs(text):
    # Padrão do CNPJ: XX.XXX.XXX/XXXX-XX
    cnpj_pattern = re.compile(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}')
    return cnpj_pattern.findall(text)

def process_pdf(file_path):
    with open(file_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        all_text = ""
        
        # Extrai texto de todas as páginas
        for page in pdf_reader.pages:
            all_text += page.extract_text() + " "
            
        cnpjs = extract_all_cnpjs(all_text)
        
        # Remove CNPJs duplicados mantendo a ordem
        unique_cnpjs = []
        seen = set()
        for cnpj in cnpjs:
            if cnpj not in seen:
                seen.add(cnpj)
                unique_cnpjs.append(cnpj)
                
        return unique_cnpjs

# Processa o primeiro arquivo
print("Processando primeiro arquivo...")
arquivo1 = "06-05-2025_-_SINGULAR_FACILITIES_SERVICE_S.A_-_ROOFTOP_CANUTO_1000_-_10325325.pdf"
cnpjs_arquivo1 = process_pdf(arquivo1)

print(f"CNPJs encontrados no primeiro arquivo ({len(cnpjs_arquivo1)}):")
for i, cnpj in enumerate(cnpjs_arquivo1, 1):
    print(f"{i}. {cnpj}")

print("\n" + "="*50 + "\n")

# Processa o segundo arquivo
print("Processando segundo arquivo...")
arquivo2 = "ROOFTOP CANUTO 1000 - 20037.pdf"
cnpjs_arquivo2 = process_pdf(arquivo2)

print(f"CNPJs encontrados no segundo arquivo ({len(cnpjs_arquivo2)}):")
for i, cnpj in enumerate(cnpjs_arquivo2, 1):
    print(f"{i}. {cnpj}")