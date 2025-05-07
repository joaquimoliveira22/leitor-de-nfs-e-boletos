import os
import PyPDF2
import re
from tqdm import tqdm

def extract_cnpjs(text):
    """Extrai todos os CNPJs de um texto"""
    pattern = re.compile(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}')
    return pattern.findall(text)

def extract_ceps(text):
    """Extrai todos os CEPs de um texto"""
    pattern = re.compile(r'\d{5}-\d{3}')
    return pattern.findall(text)

def get_cnpjs_and_ceps_from_pdf(pdf_path):
    """Extrai CNPJs e CEPs de um arquivo PDF"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''.join([page.extract_text() or '' for page in reader.pages])
            cnpjs = extract_cnpjs(text)
            ceps = extract_ceps(text)
            return cnpjs, ceps
    except Exception as e:
        print(f"\nErro ao processar '{pdf_path}': {str(e)}")
        return [], []

def main():
    # Diretório onde o script está localizado
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Lista de arquivos PDF no diretório atual
    pdf_files = [f for f in os.listdir(current_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        print("Nenhum arquivo PDF encontrado no diretório atual!")
        return
    
    # Dicionário para armazenar os CNPJs e CEPs encontrados: {nome_arquivo: (cnpjs, ceps)}
    data_by_file = {}
    
    # Processar cada PDF e extrair CNPJs e CEPs
    with tqdm(pdf_files, desc="Processando PDFs", unit="arquivo") as pbar:
        for filename in pbar:
            filepath = os.path.join(current_dir, filename)
            cnpjs, ceps = get_cnpjs_and_ceps_from_pdf(filepath)
            data_by_file[filename] = (cnpjs, ceps)
    
    # Exibir relatório
    print("\n" + "="*50)
    print("Relatório de CNPJs e CEPs encontrados:")
    total_cnpjs = 0
    total_ceps = 0
    for filename, (cnpjs, ceps) in data_by_file.items():
        print(f"\nArquivo: {filename}")
        if cnpjs or ceps:
            if cnpjs:
                for i, cnpj in enumerate(cnpjs, 1):
                    print(f"  {i}. CNPJ: {cnpj}")
                total_cnpjs += len(cnpjs)
            if ceps:
                for i, cep in enumerate(ceps, 1):
                    print(f"  {i}. CEP: {cep}")
                total_ceps += len(ceps)
        else:
            print("  Nenhum CNPJ ou CEP encontrado.")
    
    print("\n" + "="*50)
    print(f"Total de arquivos processados: {len(pdf_files)}")
    print(f"Total de CNPJs encontrados: {total_cnpjs}")
    print(f"Total de CEPs encontrados: {total_ceps}")
    print(f"Diretório processado: {current_dir}")

if __name__ == "__main__":
    main()