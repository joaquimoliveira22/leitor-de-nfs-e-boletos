import os
import PyPDF2
import re
import shutil
from tqdm import tqdm

def extract_cnpjs(text):
    pattern = re.compile(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}')
    return pattern.findall(text)

def get_third_cnpj(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''.join([page.extract_text() or '' for page in reader.pages])
            cnpjs = extract_cnpjs(text)
            return cnpjs[2] if len(cnpjs) > 2 else None
    except Exception as e:
        print(f"\nErro ao processar '{pdf_path}': {str(e)}")
        return None

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    pdf_files = [f for f in os.listdir(current_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("Nenhum arquivo PDF encontrado no diretório atual!")
        return
    
    with tqdm(pdf_files, desc="Organizando PDFs", unit="arquivo") as pbar:
        for filename in pbar:
            filepath = os.path.join(current_dir, filename)
            third_cnpj = get_third_cnpj(filepath)
            
            subfolder_name = third_cnpj.replace('.', '').replace('/', '').replace('-', '') if third_cnpj else "SEM_TERCER_CNPJ"
            subfolder_path = os.path.join(current_dir, subfolder_name)
            
            os.makedirs(subfolder_path, exist_ok=True)
            
            dest_path = os.path.join(subfolder_path, filename)
            if os.path.exists(filepath):
                shutil.move(filepath, dest_path)
            else:
                print(f"\nAviso: Arquivo '{filepath}' não encontrado. Pulando...")
    
    print("\n" + "="*50)
    print("Relatório de organização:")
    subfolders = [d for d in os.listdir(current_dir) if os.path.isdir(os.path.join(current_dir, d))]
    for subfolder in subfolders:
        pdf_count = len([f for f in os.listdir(os.path.join(current_dir, subfolder)) if f.lower().endswith('.pdf')])
        print(f"Pasta '{subfolder}': {pdf_count} PDFs")
    
    print("\n" + "="*50)
    print(f"Total de subpastas criadas: {len(subfolders)}")
    print(f"Diretório processado: {current_dir}")

if __name__ == "__main__":
    main()