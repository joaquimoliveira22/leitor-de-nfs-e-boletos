import os
import shutil
from typing import List
import re

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
            """
            O nome dos arquivos ficam grandes demais, por causa do nome das pastas, gerando erro na hora de mudar,
            por isso, no nome dos arquivos será salvo apenas a data e o número do boleto, sendo estes
            arquivo.split('-')[0:3] e arquivo.split('-')[-1], respectivamente.
            """
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
        """
        Inicializa o organizador de documentos
        
        Args:
            nfs_dir (str): Diretório das notas fiscais
            dest_dir (str): Diretório de destino (padrão: 'Documentos_Organizados')
        """
        self.nfs_dir = os.path.abspath(nfs_dir)
        self.dest_dir = os.path.abspath(dest_dir)
        
    def _extrair_nome_empresa(self, nome_arquivo: str) -> str:
        """
        Extrai o nome da empresa do nome do arquivo
        
        Args:
            nome_arquivo (str): Nome do arquivo PDF
            
        Returns:
            str: Nome da empresa extraído
        """
        # Remove extensão e caracteres especiais
        nome_sem_ext = os.path.splitext(nome_arquivo)[0]
        nome_limpo = re.sub(r'[^a-zA-Z0-9 ]', ' ', nome_sem_ext)
        
        # Divide em partes e pega a primeira parte significativa
        partes = [p for p in nome_limpo.split() if not p.isdigit()]
        return ' '.join(partes[:2]).strip() if partes else 'OUTROS'
    
    def _extrair_numero_final(self, nome_arquivo: str) -> str:
        """
        Extrai a última sequência numérica do nome do arquivo
        
        Args:
            nome_arquivo (str): Nome do arquivo PDF
            
        Returns:
            str: Última sequência numérica encontrada
        """
        numeros = re.findall(r'\d+', nome_arquivo)
        return numeros[-1] if numeros else '0000'
    
    def _criar_pasta_segura(self, caminho: str) -> bool:
        """
        Cria uma pasta com tratamento de erros
        
        Args:
            caminho (str): Caminho da pasta a ser criada
            
        Returns:
            bool: True se criada com sucesso, False caso contrário
        """
        try:
            os.makedirs(caminho, exist_ok=True)
            return True
        except Exception as e:
            print(f"Erro ao criar pasta {caminho}: {e}")
            return False
    
    def processar_notas_fiscais(self) -> None:
        """
        Processa todos os arquivos PDF de notas fiscais, organizando em pastas por empresa
        e renomeando os arquivos conforme especificado
        """
        if not os.path.exists(self.nfs_dir):
            print(f"Diretório de notas fiscais não encontrado: {self.nfs_dir}")
            return
        
        # Criar diretório principal se não existir
        self._criar_pasta_segura(self.dest_dir)
        
        # Processar cada arquivo PDF
        for arquivo in os.listdir(self.nfs_dir):
            if not arquivo.lower().endswith('.pdf'):
                continue
                
            try:
                # Extrair informações do nome do arquivo
                nome_empresa = self._extrair_nome_empresa(arquivo)
                numero_final = self._extrair_numero_final(arquivo)
                
                # Definir caminhos
                pasta_empresa = os.path.join(self.dest_dir, nome_empresa)
                novo_nome = f"{nome_empresa.split()[0]}_{numero_final}.pdf"
                caminho_destino = os.path.join(pasta_empresa, novo_nome)
                
                # Criar pasta e copiar arquivo
                if self._criar_pasta_segura(pasta_empresa):
                    caminho_origem = os.path.join(self.nfs_dir, arquivo)
                    shutil.copy2(caminho_origem, caminho_destino)
                    print(f"Organizado: {arquivo} -> {caminho_destino}")
                    
            except Exception as e:
                print(f"Erro ao processar {arquivo}: {e}")
    
    def executar(self) -> None:
        """
        Executa o fluxo completo de organização
        """
        print(f"Iniciando organização de notas fiscais...")
        print(f"Origem: {self.nfs_dir}")
        print(f"Destino: {self.dest_dir}\n")
        
        self.processar_notas_fiscais()
        
        print("\nOrganização concluída com sucesso!")

if __name__ == "__main__":
    try:
        # Configuração dos diretórios
        diretorio_notas = 'CONDOMINIAIS/NOTA_FISCAL'
        diretorio_destino = 'Arquivos/NOTA_FISCAL'
        
        # Executar organização
        organizador = OrganizadorDocumentos(diretorio_notas, diretorio_destino)
        organizador.executar()
        
    except Exception as e:
        print(f"Erro durante a execução: {e}")
    finally:
        input("Pressione Enter para sair...")
