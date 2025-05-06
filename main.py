import os
import shutil
import re
from typing import List
from tqdm import tqdm  
import difflib

class Aut:
    def __init__(self, bol_dir:  str, dest: str = 'Arquivos') -> None:
        self.bol_dir = bol_dir  # Diretório dos boletos.
          # Diretório das notas fiscais.
        self.dest = dest  # Diretório de destino dos arquivos.
        self.dest_bol = f'{dest}/BOLETOS'  # Diretório de destino dos boletos.
         # Diretório de destino das notas fiscais.

    def init_dir(self) -> None:
        """Inicializa o diretório de destino dos arquivos."""
        if not os.path.exists(self.dest):
            os.mkdir(self.dest)
            os.mkdir(self.dest_bol)
           

    def processa_boletos(self) -> None:
        # Lista os arquivos do diretório de boletos.
        arquivos: List[str] = os.listdir(self.bol_dir)
        # Padroniza o nome dos arquivos, já que alguns tem '_' no lugar de ' ' entre os itens.
        arquivos_tratados: List[str] = [arquivo.replace('_', ' ') for arquivo in arquivos]
        # Separa as informações de cada arquivo.
        arquivos_tratados: List[List[str]] = [arquivo.split('-') for arquivo in arquivos_tratados]
        # Remove as informações de dia e número de boleto de cada arquivo.
        arquivos_tratados: List[List[str]] = [arquivo[1:-1] for arquivo in arquivos_tratados]
        # Converte cada arquivo que está como lista em string novamente.
        arquivos_tratados: List[str] = [' '.join(arquivo) for arquivo in arquivos_tratados]
        # Remove espaços excedentes no meio dos arquivos.
        arquivos_tratados = [' '.join([nome.strip() for nome in arquivo.split()]) for arquivo in arquivos_tratados]

        # Percorre cada arquivo e nome_tratado ao mesmo tempo.
        for arquivo, nome in zip(arquivos, arquivos_tratados):
            dest_dir: str = f'{self.dest_bol}/{nome}'  # Pasta de destino para o arquivo atual.
            # Verifica se a pasta já existe.
            if not os.path.exists(dest_dir):
                os.mkdir(dest_dir)
            # Adiciona ao nome do arquivo a pasta onde está, para poder ser encontrado.
            old_path = f'{self.bol_dir}/{arquivo}'
      
            new_path = f'{dest_dir}/{arquivo.split('-')[0]}-{arquivo.split('-')[-1]}'
            # Move o arquivo atual para a sua pasta.
            shutil.copy(old_path, new_path)

    def run(self) -> None:
        self.init_dir()
        self.processa_boletos()


if __name__ == "__main__":
    try:
        bol_dir = 'CONDOMINIAIS/BOLETOS'
        
        aut = Aut(bol_dir)
        aut.run()
    except Exception as e:
        print(e)
        input()


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
        
        arquivos = [arq for arq in os.listdir(self.nfs_dir) if arq.lower().endswith('.pdf')]
        
        # Usando tqdm para mostrar progresso
        for arquivo in tqdm(arquivos, desc="Processando notas fiscais"):
                
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


class OrganizadorDocumentosPorRelacao:
    def __init__(self, boletos_dir='Arquivos/BOLETOS', notas_dir='Arquivos/NOTA_FISCAL', destino='Arquivos/ORGANIZADOS'):
        self.boletos_dir = os.path.abspath(boletos_dir)
        self.notas_dir = os.path.abspath(notas_dir)
        self.destino = os.path.abspath(destino)
        
    def _normalizar_nome(self, nome):
        """Normaliza nomes para facilitar comparação"""
        # Remove caracteres especiais e converte para minúsculas
        nome_limpo = re.sub(r'[^a-zA-Z0-9]', '', nome).lower()
        return nome_limpo
        
    def _verificar_semelhanca(self, nome1, nome2, threshold=0.6):
        """Verifica se dois nomes têm semelhança usando difflib"""
        nome1_norm = self._normalizar_nome(nome1)
        nome2_norm = self._normalizar_nome(nome2)
        
        # Primeiro tenta encontrar um contido no outro
        if nome1_norm in nome2_norm or nome2_norm in nome1_norm:
            return True
            
        # Caso contrário, usa a métrica de semelhança
        ratio = difflib.SequenceMatcher(None, nome1_norm, nome2_norm).ratio()
        return ratio > threshold
        
    def _criar_pasta_segura(self, caminho):
        """Cria pastas de forma segura"""
        try:
            os.makedirs(caminho, exist_ok=True)
            return True
        except Exception as e:
            print(f"Erro ao criar pasta {caminho}: {e}")
            return False
            
    def _copiar_pasta(self, origem, destino):
        """Copia uma pasta e seu conteúdo para o destino"""
        if not os.path.exists(destino):
            try:
                shutil.copytree(origem, destino)
                return True
            except Exception as e:
                print(f"Erro ao copiar pasta {origem} para {destino}: {e}")
                return False
        return False
        
    def organizar(self):
        """Função principal para organizar os documentos"""
        print(f"Iniciando organização de documentos...")
        
        # Verifica se os diretórios existem
        if not os.path.exists(self.boletos_dir):
            print(f"Diretório de boletos não encontrado: {self.boletos_dir}")
            return
            
        if not os.path.exists(self.notas_dir):
            print(f"Diretório de notas fiscais não encontrado: {self.notas_dir}")
            return
            
        # Cria diretório de destino
        self._criar_pasta_segura(self.destino)
        
        # Lista pastas de boletos e notas fiscais
        pastas_boletos = [d for d in os.listdir(self.boletos_dir) 
                         if os.path.isdir(os.path.join(self.boletos_dir, d))]
        
        pastas_notas = [d for d in os.listdir(self.notas_dir) 
                        if os.path.isdir(os.path.join(self.notas_dir, d))]
        
        # Para cada pasta de boleto, procura correspondência nas notas fiscais
        for boleto in pastas_boletos:
            for nota in pastas_notas:
                if self._verificar_semelhanca(boleto, nota):
                    # Encontrou relação, cria pasta unificada
                    nome_unificado = f"{boleto}_{nota}"
                    pasta_unificada = os.path.join(self.destino, nome_unificado)
                    
                    if self._criar_pasta_segura(pasta_unificada):
                        # Cria subpastas
                        pasta_boleto_dest = os.path.join(pasta_unificada, "BOLETOS")
                        pasta_nota_dest = os.path.join(pasta_unificada, "NOTAS_FISCAIS")
                        
                        # Copia conteúdo
                        origem_boleto = os.path.join(self.boletos_dir, boleto)
                        origem_nota = os.path.join(self.notas_dir, nota)
                        
                        if self._copiar_pasta(origem_boleto, pasta_boleto_dest):
                            print(f"Boleto copiado: {boleto}")
                        
                        if self._copiar_pasta(origem_nota, pasta_nota_dest):
                            print(f"Nota fiscal copiada: {nota}")
                            
                        print(f"Relação encontrada e organizada: {boleto} <-> {nota}")
        
        print("\nOrganização concluída com sucesso!")

if __name__ == "__main__":
    try:
        organizador = OrganizadorDocumentosPorRelacao()
        organizador.organizar()
    except Exception as e:
        print(f"Erro durante a execução: {e}")
    finally:
        input("Pressione Enter para sair...")
