import os
import shutil
import re
from typing import List

class OrganizadorDocumentos:
    def __init__(self, nfs_dir: str, dest_dir: str = 'Arquivos/NOTA_FISCAL') -> None:
       
        self.nfs_dir = os.path.abspath(nfs_dir)
        self.dest_dir = os.path.abspath(dest_dir)
        
    def _extrair_nome_empresa(self, nome_arquivo: str) -> str:
       
        nome_sem_ext = os.path.splitext(nome_arquivo)[0]
        nome_limpo = re.sub(r'[^a-zA-Z0-9 ]', ' ', nome_sem_ext)
        
        partes = [p for p in nome_limpo.split() if not p.isdigit()]
        return ' '.join(partes[:2]).strip() if partes else 'OUTROS'
    
    def _extrair_numero_final(self, nome_arquivo: str) -> str:
     
        numeros = re.findall(r'\d+', nome_arquivo)
        return numeros[-1] if numeros else '0000'
    
    def _remover_numeros_finais(self, nome_arquivo: str) -> str:
        # Remove a extensão do arquivo
        nome_sem_ext = os.path.splitext(nome_arquivo)[0]
        
        # Remove números no final do nome
        nome_sem_numeros_finais = re.sub(r'\d+$', '', nome_sem_ext)
        
        # Remove espaços em excesso
        nome_limpo = nome_sem_numeros_finais.strip()
        
        return nome_limpo
    
    def _criar_pasta_segura(self, caminho: str) -> bool:
      
        try:
            os.makedirs(caminho, exist_ok=True)
            return True
        except Exception as e:
            print(f"Erro ao criar pasta {caminho}: {e}")
            return False
    
    def processar_notas_fiscais(self) -> None:
       
        if not os.path.exists(self.nfs_dir):
            print(f"Diretório de notas fiscais não encontrado: {self.nfs_dir}")
            return
        
        self._criar_pasta_segura(self.dest_dir)
        
        for arquivo in os.listdir(self.nfs_dir):
            if not arquivo.lower().endswith('.pdf'):
                continue
                
            try:
                nome_empresa = self._extrair_nome_empresa(arquivo)
                
                # Novo nome usando o nome completo sem números finais
                nome_sem_numeros = self._remover_numeros_finais(arquivo)
                novo_nome = f"{nome_sem_numeros}.pdf"
                
                pasta_empresa = os.path.join(self.dest_dir, nome_empresa)
                caminho_destino = os.path.join(pasta_empresa, novo_nome)
                
                if self._criar_pasta_segura(pasta_empresa):
                    caminho_origem = os.path.join(self.nfs_dir, arquivo)
                    shutil.copy2(caminho_origem, caminho_destino)
                    print(f"Organizado: {arquivo} -> {caminho_destino}")
                    
            except Exception as e:
                print(f"Erro ao processar {arquivo}: {e}")
    
    def executar(self) -> None:
       
        print(f"Iniciando organização de notas fiscais...")
        print(f"Origem: {self.nfs_dir}")
        print(f"Destino: {self.dest_dir}\n")
        
        self.processar_notas_fiscais()
        
        print("\nOrganização concluída com sucesso!")

if __name__ == "__main__":
    try:
        diretorio_notas = 'CONDOMINIAIS/NOTA_FISCAL'
        diretorio_destino = 'Arquivos/NOTA_FISCAL'
        
        organizador = OrganizadorDocumentos(diretorio_notas, diretorio_destino)
        organizador.executar()
        
    except Exception as e:
        print(f"Erro durante a execução: {e}")
    finally:
        input("Pressione Enter para sair...")