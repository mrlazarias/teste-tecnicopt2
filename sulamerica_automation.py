import requests
import logging
from urllib.parse import urljoin

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SulAmericaAutomation:
    
    def __init__(self):
        self.base_url = "https://saude.sulamericaseguros.com.br/prestador/"
        self.session = requests.Session()
        
        # Headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1'
        })

    def login(self, username, password, identification_code):
        """
        
        Args:
            username: Usuário para login
            password: Senha para login
            identification_code: Código de identificação do prestador
            
        Returns:
            bool: True se o login foi bem-sucedido
        """
        try:
            login_url = urljoin(self.base_url, "login")
            
            # Acessa a página de login para capturar cookies
            response = self.session.get(login_url)
            response.raise_for_status()
            
            # Atualiza o referer para o login
            self.session.headers.update({
                'Referer': login_url,
                'Origin': 'https://saude.sulamericaseguros.com.br'
            })
            
            # Prepara os dados de login
            login_data = {
                'usuario': username,
                'senha': password,
                'codigoReferenciado': identification_code
            }
            
            # Realiza o login
            login_response = self.session.post(login_url, data=login_data)
            login_response.raise_for_status()
            
            # Verifica se o login foi bem-sucedido
            if "accessError" in login_response.url:
                logger.error("Falha no login - Verifique as credenciais")
                return False
                
            logger.info("Login realizado com sucesso")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Falha no login: {str(e)}")
            return False

    def buscar_beneficiario(self, beneficiary_code, username=None, password=None, identification_code=None):
        """
        
        Args:
            beneficiary_code: Código do beneficiário (carteira)
            username, password, identification_code: Credenciais para possível relogin
            
        Returns:
            bool: True se a busca foi bem-sucedida
        """
        try:
            logger.info("Acessando menu Serviços Médicos > Faturamento > Guia de Consulta...")
            
            # Rota conforme especificações
            target_url = urljoin(self.base_url, "servicos-medicos/contas-medicas/faturamento/guia-de-consulta")
            
            # Obtém a página
            response = self.session.get(target_url)
            if response.status_code != 200:
                logger.error(f"Erro ao acessar página de guia: {response.status_code}")
                return False
            
            # Separa o código do beneficiário em blocos de 5 dígitos
            code_parts = [beneficiary_code[i:i+5] for i in range(0, len(beneficiary_code), 5)]
            
            # Prepara os dados para busca
            search_data = {
                'digiteCodigo_1': code_parts[0],
                'digiteCodigo_2': code_parts[1],
                'digiteCodigo_3': code_parts[2],
                'digiteCodigo_4': code_parts[3],
                'confirmar': 'Confirmar'
            }
            
            # Envia o formulário
            logger.info(f"Buscando beneficiário: {beneficiary_code}")
            submit_response = self.session.post(target_url, data=search_data)
            
            if submit_response.status_code != 200:
                logger.error(f"Erro ao buscar beneficiário: {submit_response.status_code}")
                return False
            
            # Se a sessão expirou, tenta fazer login novamente
            if "login" in submit_response.url or "accessError" in submit_response.url:
                logger.warning("Sessão expirou, realizando login novamente...")
                
                # Tenta fazer login novamente e repete a busca
                if username and password and identification_code:
                    if self.login(username, password, identification_code):
                        logger.info("Login renovado, tentando busca novamente...")
                        
                        # Acessa e submete o formulário novamente
                        response = self.session.get(target_url)
                        if response.status_code != 200:
                            return False
                        
                        submit_response = self.session.post(target_url, data=search_data)
                        if submit_response.status_code != 200:
                            return False
            
            logger.info(f"Beneficiário {beneficiary_code} localizado com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao buscar beneficiário: {str(e)}")
            return False

def main():
    
    # Inicializa a automação
    automation = SulAmericaAutomation()
    
    # Credenciais conforme especificadas
    username = "master"
    password = "837543"
    identification_code = "100000009361"
    
    # Código do beneficiário (número da carteira)
    beneficiary_code = "55788888485177660015"
    
    # Realiza login e busca o beneficiário
    if automation.login(username, password, identification_code):
        if automation.buscar_beneficiario(beneficiary_code, username, password, identification_code):
            logger.info("Automação concluída com sucesso!")
        else:
            logger.error("Falha ao buscar beneficiário")
    else:
        logger.error("Falha no processo de login")

if __name__ == "__main__":
    main() 