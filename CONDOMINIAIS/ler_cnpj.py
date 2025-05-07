import os
import PyPDF2
import re
import shutil

def extract_all_cnpjs(text):
    cnpj_pattern = re.compile(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}')
    return cnpj_pattern.findall(text)

def process_pdf(file_path):
    with open(file_path, "rb") as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        all_text = ""
        
        for page in pdf_reader.pages:
            all_text += page.extract_text() + " "
            
        cnpjs = extract_all_cnpjs(all_text)
        
        unique_cnpjs = []
        seen = set()
        for cnpj in cnpjs:
            if cnpj not in seen:
                seen.add(cnpj)
                unique_cnpjs.append(cnpj)
                
        return unique_cnpjs

print("Processando primeiro arquivo...")
arquivo1 = "06-05-2025_-_SINGULAR_FACILITIES_SERVICE_S.A_-_ROOFTOP_CANUTO_1000_-_10325325.pdf"
cnpjs_arquivo1 = process_pdf(arquivo1)

print(f"CNPJs encontrados no primeiro arquivo ({len(cnpjs_arquivo1)}):")
for i, cnpj in enumerate(cnpjs_arquivo1, 1):
    print(f"{i}. {cnpj}")

print("\n" + "="*50 + "\n")

print("Processando segundo arquivo...")
arquivo2 = "ROOFTOP CANUTO 1000 - 20037.pdf"
cnpjs_arquivo2 = process_pdf(arquivo2)

print(f"CNPJs encontrados no segundo arquivo ({len(cnpjs_arquivo2)}):")
for i, cnpj in enumerate(cnpjs_arquivo2, 1):
    print(f"{i}. {cnpj}")




def create_folder_and_copy_if_matching(cnpjs1, cnpjs2, file1, file2):
    # Verifica se há CNPJs em ambos os arquivos e se todos são iguais
    if cnpjs1 and cnpjs2 and set(cnpjs1) == set(cnpjs2):
        print("\nTodos os CNPJs são iguais nos dois arquivos!")
        
        # Cria o nome da pasta com o primeiro CNPJ (sem pontuação)
        cnpj_folder_name = cnpjs1[0].replace('.', '').replace('/', '').replace('-', '')
        folder_name = f"CNPJ_{cnpj_folder_name}"
        
        # Cria a pasta se não existir
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
            print(f"Pasta '{folder_name}' criada.")
        
        # Copia os arquivos para a nova pasta
        shutil.copy2(file1, folder_name)
        shutil.copy2(file2, folder_name)
        print(f"Arquivos copiados para a pasta '{folder_name}'.")
        
        return True
    else:
        print("\nOs CNPJs não são todos iguais nos dois arquivos.")
        return False

# Verifica e copia se todos os CNPJs forem iguais
create_folder_and_copy_if_matching(cnpjs_arquivo1, cnpjs_arquivo2, arquivo1, arquivo2)
    