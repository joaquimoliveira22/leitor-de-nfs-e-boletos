import os
import PyPDF2
import re
import shutil
from tqdm import tqdm
from colorama import init, Fore, Style

# Inicializa o colorama para suporte a cores no terminal
init()

def extract_cnpjs(text):
    """Extrai todos os CNPJs de um texto"""
    pattern = re.compile(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}')
    return pattern.findall(text)

def get_second_cnpj(pdf_path):
    """Obtém o segundo CNPJ encontrado no arquivo PDF ou None se não houver"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''.join([page.extract_text() or '' for page in reader.pages])
            cnpjs = extract_cnpjs(text)
            return cnpjs[1] if len(cnpjs) > 1 else None
    except Exception as e:
        print(f"\nErro ao processar '{pdf_path}': {str(e)}")
        return None

def get_third_cnpj(pdf_path):
    """Obtém o terceiro CNPJ encontrado no arquivo PDF ou None se não houver"""
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''.join([page.extract_text() or '' for page in reader.pages])
            cnpjs = extract_cnpjs(text)
            return cnpjs[2] if len(cnpjs) > 2 else None
    except Exception as e:
        print(f"\nErro ao processar '{pdf_path}': {str(e)}")
        return None

def process_files(folder_path, file_type):
    """Processa todos os arquivos PDF de uma pasta e retorna dicionário {cnpj: [arquivos]}"""
    cnpj_dict = {}
    pdf_files = [f for f in os.listdir(folder_path) if f.lower().endswith('.pdf')]
    
    with tqdm(pdf_files, desc=f"{Fore.GREEN}Processando {file_type}{Style.RESET_ALL}", unit="arquivo") as pbar:
        for filename in pbar:
            filepath = os.path.join(folder_path, filename)
            try:
                cnpj = get_second_cnpj(filepath)
                if cnpj:
                    if cnpj not in cnpj_dict:
                        cnpj_dict[cnpj] = []
                    cnpj_dict[cnpj].append(filename)
                else:
                    print(f"\nAviso: {file_type} '{filename}' não contém um segundo CNPJ válido")
            except Exception as e:
                print(f'\nErro ao processar {filename}: {str(e)}')
    
    return cnpj_dict

def organize_files_by_second_cnpj(boletos_dict, nfs_dict, output_folder, boletos_dir, nfs_dir):
    """Organiza boletos e notas fiscais nas pastas conforme os requisitos"""
    os.makedirs(output_folder, exist_ok=True)
    
    # Processar CNPJs com boletos e NFs correspondentes
    common_cnpjs = set(boletos_dict.keys()) & set(nfs_dict.keys())
    with tqdm(common_cnpjs, desc=f"{Fore.YELLOW}Arquivos com boletos correspondentes{Style.RESET_ALL}", unit="CNPJ") as pbar:
        for cnpj in pbar:
            folder_name = cnpj.replace('.', '').replace('/', '').replace('-', '')
            folder_path = os.path.join(output_folder, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            
            for boleto in boletos_dict[cnpj]:
                src_path = os.path.join(boletos_dir, boleto)
                dst_path = os.path.join(folder_path, boleto)
                if os.path.exists(src_path):
                    shutil.copy2(src_path, dst_path)
                else:
                    print(f"\nAviso: Boleto '{src_path}' não encontrado. Pulando...")
            
            for nf in nfs_dict[cnpj]:
                src_path = os.path.join(nfs_dir, nf)
                dst_path = os.path.join(folder_path, nf)
                if os.path.exists(src_path):
                    shutil.copy2(src_path, dst_path)
                else:
                    print(f"\nAviso: NF '{src_path}' não encontrado. Pulando...")
    
    # Processar NFs sem boletos correspondentes
    nfs_only_cnpjs = set(nfs_dict.keys()) - set(boletos_dict.keys())
    with tqdm(nfs_only_cnpjs, desc=f"{Fore.BLUE}NFs sem boletos correspondentes{Style.RESET_ALL}", unit="CNPJ") as pbar:
        for cnpj in pbar:
            if cnpj:  # Ignora None
                folder_name = f"NF_{cnpj.replace('.', '').replace('/', '').replace('-', '')}"
                folder_path = os.path.join(output_folder, folder_name)
                os.makedirs(folder_path, exist_ok=True)
                
                for nf in nfs_dict[cnpj]:
                    src_path = os.path.join(nfs_dir, nf)
                    dst_path = os.path.join(folder_path, nf)
                    if os.path.exists(src_path):
                        shutil.copy2(src_path, dst_path)
                    else:
                        print(f"\nAviso: NF '{src_path}' não encontrado. Pulando...")
    
    # Processar NFs sem CNPJ identificável
    nfs_without_cnpj = []
    for nf_list in nfs_dict.values():
        for nf in nf_list:
            filepath = os.path.join(nfs_dir, nf)
            if get_second_cnpj(filepath) is None:
                nfs_without_cnpj.append(nf)
    
    if nfs_without_cnpj:
        folder_path = os.path.join(output_folder, "NFs_SEM_CNPJ_IDENTIFICADO")
        os.makedirs(folder_path, exist_ok=True)
        print("\nOrganizando NFs sem CNPJ identificável...")
        for nf in nfs_without_cnpj:
            src_path = os.path.join(nfs_dir, nf)
            dst_path = os.path.join(folder_path, nf)
            if os.path.exists(src_path):
                shutil.copy2(src_path, dst_path)
            else:
                print(f"\nAviso: NF '{src_path}' não encontrado. Pulando...")

def organize_files_by_third_cnpj(current_dir, exclude_folders=None):
    """Organiza PDFs no diretório atual em subpastas baseadas no terceiro CNPJ"""
    if exclude_folders is None:
        exclude_folders = set()
    
    # Lista de arquivos PDF no diretório atual, excluindo os das pastas BOLETOS, NOTA_FISCAL e ORGANIZADOS
    pdf_files = [
        f for f in os.listdir(current_dir) 
        if f.lower().endswith('.pdf') and f not in exclude_folders
        and not os.path.isdir(os.path.join(current_dir, f))
    ]
    
    if not pdf_files:
        print(f"\n{Fore.CYAN}Nenhum arquivo PDF adicional encontrado no diretório atual para organizar pelo terceiro CNPJ!{Style.RESET_ALL}")
        return
    
    # Processar cada PDF e organizar em subpastas
    with tqdm(pdf_files, desc=f"{Fore.MAGENTA}Organizando PDFs pelo terceiro CNPJ{Style.RESET_ALL}", unit="arquivo") as pbar:
        for filename in pbar:
            filepath = os.path.join(current_dir, filename)
            third_cnpj = get_third_cnpj(filepath)
            
            # Define o nome da subpasta com base no terceiro CNPJ
            subfolder_name = third_cnpj.replace('.', '').replace('/', '').replace('-', '') if third_cnpj else "SEM_TERCER_CNPJ"
            subfolder_path = os.path.join(current_dir, subfolder_name)
            
            # Cria a subpasta se não existir
            os.makedirs(subfolder_path, exist_ok=True)
            
            # Move o arquivo para a subpasta correspondente
            dest_path = os.path.join(subfolder_path, filename)
            if os.path.exists(filepath):
                shutil.move(filepath, dest_path)
            else:
                print(f"\nAviso: Arquivo '{filepath}' não encontrado. Pulando...")

def main():
    # Diretório onde o script está localizado
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Definir pastas com caminhos absolutos
    BOLETOS_DIR = os.path.abspath(os.path.join(current_dir, "BOLETOS"))
    NFS_DIR = os.path.abspath(os.path.join(current_dir, "NOTA_FISCAL"))
    OUTPUT_DIR = os.path.abspath(os.path.join(current_dir, "ORGANIZADOS"))
    
    # Verificar se as pastas BOLETOS e NOTA_FISCAL existem
    boletos_nfs_processed = False
    if not os.path.exists(BOLETOS_DIR):
        print(f"Aviso: Pasta '{BOLETOS_DIR}' não encontrada! Pulando organização de boletos e NFs.")
    elif not os.path.exists(NFS_DIR):
        print(f"Aviso: Pasta '{NFS_DIR}' não encontrada! Pulando organização de boletos e NFs.")
    else:
        print(f"\n{Fore.GREEN}Iniciando processamento de boletos e notas fiscais...{Style.RESET_ALL}")
        boletos_dict = process_files(BOLETOS_DIR, "boletos")
        nfs_dict = process_files(NFS_DIR, "notas fiscais")
        organize_files_by_second_cnpj(boletos_dict, nfs_dict, OUTPUT_DIR, BOLETOS_DIR, NFS_DIR)
        boletos_nfs_processed = True
    
    # Organizar outros PDFs no diretório atual pelo terceiro CNPJ
    exclude_folders = {"BOLETOS", "NOTA_FISCAL", "ORGANIZADOS"}
    organize_files_by_third_cnpj(current_dir, exclude_folders)
    
    # Gerar relatório
    print("\n" + "="*50)
    print("Relatório de organização:")
    
    # Relatório para boletos e NFs
    if boletos_nfs_processed:
        print(f"\n{Fore.GREEN}Organização de Boletos e Notas Fiscais (baseada no segundo CNPJ):{Style.RESET_ALL}")
        print(f"- Pastas com boletos e NFs: {len(set(boletos_dict.keys()) & set(nfs_dict.keys()))}")
        print(f"- Pastas apenas com NFs: {len(set(nfs_dict.keys()) - set(boletos_dict.keys()))}")
        print(f"- NFs sem CNPJ identificável: {len([nf for nf_list in nfs_dict.values() for nf in nf_list if get_second_cnpj(os.path.join(NFS_DIR, nf)) is None])}")
        print(f"Resultado em: {OUTPUT_DIR}")
    
    # Relatório para PDFs organizados pelo terceiro CNPJ
    print(f"\n{Fore.MAGENTA}Organização de outros PDFs (baseada no terceiro CNPJ):{Style.RESET_ALL}")
    subfolders = [
        d for d in os.listdir(current_dir) 
        if os.path.isdir(os.path.join(current_dir, d)) and d not in exclude_folders
    ]
    for subfolder in subfolders:
        pdf_count = len([f for f in os.listdir(os.path.join(current_dir, subfolder)) if f.lower().endswith('.pdf')])
        print(f"Pasta '{subfolder}': {pdf_count} PDFs")
    
    print("\n" + "="*50)
    print(f"Total de subpastas criadas (terceiro CNPJ): {len(subfolders)}")
    print(f"Diretório processado: {current_dir}")

if __name__ == "__main__":
    main()