import os
import shutil
import re
import difflib

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
