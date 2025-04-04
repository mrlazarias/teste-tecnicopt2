import requests
from bs4 import BeautifulSoup
import re
import json
import time

class SulAmericaAutomacao:
    def __init__(self):
        # URLs importantes
        self.login_url = "https://saude.sulamericaseguros.com.br/prestador/login/"
        self.guia_consulta_url = "https://saude.sulamericaseguros.com.br/prestador/servicos-medicos/contas-medicas/faturamento-tiss-3/faturamento/guia-de-consulta/"
        
        # Credenciais de acesso
        self.usuario = "master"
        self.senha = "837543"
        self.codigo_referenciado = "100000009361"
        
        # Número da carteira do paciente
        self.numero_carteira = "55788888485177660015"
        
        # Sessão para manter cookies e headers
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })

    def salvar_html_para_debug(self, html, nome_arquivo):
        """Salva o HTML recebido em um arquivo para debug"""
        with open(f"{nome_arquivo}.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"HTML salvo no arquivo {nome_arquivo}.html para debug")

    def encontrar_form_action(self, soup):
        """Encontra a URL de ação do formulário de login"""
        login_form = None
        # Procurar por formulários
        forms = soup.find_all('form')
        print(f"Encontrados {len(forms)} formulários na página")
        
        for i, form in enumerate(forms):
            print(f"Formulário {i+1}:")
            print(f"  Action: {form.get('action', 'Não especificado')}")
            print(f"  ID: {form.get('id', 'Não especificado')}")
            print(f"  Método: {form.get('method', 'Não especificado')}")
            
            # Verificar se esse é o formulário de login
            # Procurar campos de usuário/senha que são típicos de login
            username_field = form.find('input', {'type': 'text', 'name': re.compile(r'(user|login|username|code)', re.I)})
            password_field = form.find('input', {'type': 'password'})
            
            if username_field and password_field:
                login_form = form
                print(f"  Este parece ser o formulário de login! (username: {username_field.get('name')}, password: {password_field.get('name')})")
                break
        
        if login_form:
            # Obter a URL de action do formulário
            action_url = login_form.get('action')
            if not action_url or action_url == '#' or action_url == '':
                # Se não tiver action, usar a URL atual
                action_url = self.login_url
            elif not action_url.startswith('http'):
                # Se for URL relativa, transformar em absoluta
                if action_url.startswith('/'):
                    action_url = f"https://saude.sulamericaseguros.com.br{action_url}"
                else:
                    action_url = f"{self.login_url.rstrip('/')}/{action_url.lstrip('/')}"
            
            # Obter os nomes dos campos
            user_field = login_form.find('input', {'type': 'text', 'name': re.compile(r'(user|login|username|code)', re.I)})
            pass_field = login_form.find('input', {'type': 'password'})
            
            user_field_name = user_field.get('name') if user_field else None
            pass_field_name = pass_field.get('name') if pass_field else None
            
            # Retornar a URL e os nomes dos campos
            return {
                'action_url': action_url,
                'user_field': user_field_name,
                'pass_field': pass_field_name,
                'form_id': login_form.get('id', '')
            }
        
        return None

    def extrair_hidden_inputs(self, soup, form_id=None):
        """Extrai todos os inputs hidden de um formulário"""
        hidden_values = {}
        
        if form_id:
            # Se tiver ID do formulário, procurar apenas nele
            form = soup.find('form', {'id': form_id})
            if form:
                hidden_inputs = form.find_all('input', {'type': 'hidden'})
            else:
                hidden_inputs = []
        else:
            # Caso contrário, procurar em toda a página
            hidden_inputs = soup.find_all('input', {'type': 'hidden'})
        
        for hidden in hidden_inputs:
            if hidden.get('name'):
                hidden_values[hidden.get('name')] = hidden.get('value', '')
        
        return hidden_values

    def login(self):
        """Realiza o login na plataforma SulAmérica"""
        print("Iniciando processo de login...")
        
        # Primeiro acesso para obter o formulário e os campos
        try:
            response = self.session.get(self.login_url)
            response.raise_for_status()
            print(f"Resposta recebida. Status: {response.status_code}")
            print(f"Cookies recebidos: {dict(response.cookies)}")
            
            # Salvar a página para debug
            self.salvar_html_para_debug(response.text, "pagina_login")
            
            # Processar a página de login
            soup = BeautifulSoup(response.text, 'html5lib')
            print(f"Título da página: {soup.title.string if soup.title else 'Sem título'}")
            
            # Encontrar o formulário de login e extrair informações
            form_info = self.encontrar_form_action(soup)
            
            if not form_info:
                print("Não foi possível encontrar o formulário de login. Abortando login.")
                return False
            
            print(f"Formulário de login encontrado:")
            print(f"  Action URL: {form_info['action_url']}")
            print(f"  Campo de usuário: {form_info['user_field']}")
            print(f"  Campo de senha: {form_info['pass_field']}")
            
            # Extrair inputs hidden do formulário
            hidden_values = self.extrair_hidden_inputs(soup, form_info.get('form_id'))
            print(f"  Valores hidden encontrados: {len(hidden_values)}")
            
            # Preparar dados para o login
            login_data = hidden_values.copy()
            
            # Adicionar credenciais
            if form_info['user_field'] and form_info['pass_field']:
                # Verificar se o campo de usuário parece ser um campo de código
                if 'code' in form_info['user_field'].lower():
                    login_data[form_info['user_field']] = self.codigo_referenciado
                    
                    # Se temos um campo de código, precisamos encontrar o campo de usuário
                    user_field = soup.find('input', {'name': re.compile(r'(user)', re.I)})
                    if user_field:
                        login_data[user_field.get('name')] = self.usuario
                else:
                    login_data[form_info['user_field']] = self.usuario
                
                # Adicionar senha
                login_data[form_info['pass_field']] = self.senha
                
                # Verificar campos adicionais que podem ser necessários
                code_field = soup.find('input', {'name': re.compile(r'(code|codigo)', re.I)})
                if code_field and code_field.get('name') != form_info['user_field']:
                    code_field_name = code_field.get('name')
                    login_data[code_field_name] = self.codigo_referenciado
            else:
                print("Não foi possível determinar os campos de login. Tentando com valores padrão.")
                # Tentar com nomes padrão
                if soup.find('input', {'name': 'user'}):
                    login_data['user'] = self.usuario
                if soup.find('input', {'name': 'code'}):
                    login_data['code'] = self.codigo_referenciado
                login_data['senha'] = self.senha
            
            # Adicionar campos para botão de submit, se presentes
            submit_button = soup.find('button', {'type': 'submit'}) or soup.find('input', {'type': 'submit'})
            if submit_button and submit_button.get('name'):
                login_data[submit_button.get('name')] = submit_button.get('value', '')
            
            # Tratamento especial para o formulário do SulAmérica
            # Adicionar informações do que foi observado no HTML
            if 'user' not in login_data and 'code' in login_data:
                print("Detectado formulário especial SulAmérica. Adicionando campo 'user'.")
                login_data['user'] = self.usuario
            
            # Solução específica baseada na análise da página
            print("Tentando preencher campos adicionais identificados na análise:")
            if 'code' in login_data:
                print(f"  - Usando código referenciado: {self.codigo_referenciado}")
            if 'user' in login_data:
                print(f"  - Usando usuário: {self.usuario}")
            if 'senha' in login_data:
                print(f"  - Senha configurada (valor oculto)")
            
            print(f"Dados de login preparados: {json.dumps({k: v for k, v in login_data.items() if k in ['user', 'senha', 'code']}, indent=2)}")
            
            # Fazer a requisição de login
            login_url = form_info['action_url']
            # Limpar a URL para evitar problemas com redirecionamentos
            if "../../" in login_url:
                print("Detectada URL com '../../'. Corrigindo...")
                # Corrigir a URL de forma mais segura
                if login_url.startswith("../../"):
                    login_url = "https://saude.sulamericaseguros.com.br/" + login_url[6:]
                else:
                    # Tratar URLs relativas mais complexas
                    parts = login_url.split('/')
                    base_parts = []
                    for part in parts:
                        if part == "..":
                            if base_parts:
                                base_parts.pop()
                        else:
                            base_parts.append(part)
                    
                    # Reconstruir a URL
                    if base_parts and base_parts[0] == "https:" or base_parts[0] == "http:":
                        login_url = "/".join(base_parts)
                    else:
                        login_url = "https://saude.sulamericaseguros.com.br/" + "/".join(base_parts)
                
                print(f"URL corrigida: {login_url}")
            
            # Verificar se a URL é absoluta, se não for, torná-la absoluta
            if not login_url.startswith("http"):
                login_url = "https://saude.sulamericaseguros.com.br/" + login_url.lstrip("/")
                print(f"URL convertida para absoluta: {login_url}")
            
            print(f"Enviando dados de login para: {login_url}")
            
            login_response = self.session.post(
                login_url,
                data=login_data,
                headers={
                    "Referer": self.login_url,
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                allow_redirects=True  # Permitir seguir redirecionamentos
            )
            login_response.raise_for_status()
            
            # Imprimir o histórico de redirecionamentos
            print("Histórico de redirecionamentos:")
            for i, resp in enumerate(login_response.history):
                print(f"  {i+1}. {resp.status_code} -> {resp.url}")
            print(f"  Final: {login_response.status_code} -> {login_response.url}")
            
            # Salvar a resposta para análise
            self.salvar_html_para_debug(login_response.text, "pagina_apos_login")
            
            # Verificar se o login foi bem-sucedido
            login_success = False
            
            # Verificar URL
            if "login" not in login_response.url.lower():
                print("Redirecionado para fora da página de login. Login possivelmente bem-sucedido.")
                login_success = True
            
            # Verificar conteúdo da página
            success_indicators = ["logout", "bem-vindo", "area logada", "minha conta", self.usuario.lower()]
            for indicator in success_indicators:
                if indicator in login_response.text.lower():
                    print(f"Indicador de login bem-sucedido encontrado: '{indicator}'")
                    login_success = True
            
            # Verificar presença de elementos típicos pós-login
            soup_after = BeautifulSoup(login_response.text, 'html5lib')
            logout_links = soup_after.find_all('a', string=re.compile(r'(sair|logout|exit)', re.I)) or soup_after.find_all('a', {'href': re.compile(r'(logout|sair)', re.I)})
            
            if logout_links:
                print(f"Link de logout encontrado: {logout_links[0].get('href', 'sem href')}")
                login_success = True
            
            user_info = soup_after.find_all(string=re.compile(rf'({self.usuario}|{self.codigo_referenciado})', re.I))
            if user_info:
                print(f"Informações do usuário encontradas na página.")
                login_success = True
            
            if login_success:
                print("Login realizado com sucesso!")
                
                # Extrair cookies importantes que precisam ser mantidos
                print("Cookies após login:")
                for cookie_name, cookie_value in self.session.cookies.items():
                    print(f"  {cookie_name}: {cookie_value}")
                
                return True
            else:
                print("Permanecemos na página de login. Verificando mensagens de erro...")
                erro_soup = BeautifulSoup(login_response.text, 'html5lib')
                error_messages = erro_soup.find_all(['div', 'span', 'p'], {'class': re.compile(r'(alert|error|msg-erro|erro)', re.I)})
                
                if error_messages:
                    for error in error_messages:
                        print(f"Mensagem de erro encontrada: {error.get_text(strip=True)}")
                else:
                    print("Nenhuma mensagem de erro encontrada, mas o login aparentemente falhou.")
                
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar a página de login: {e}")
            return False

    def acessar_guia_consulta(self):
        """Acessa a página de Guia de Consulta"""
        print("Acessando página de Guia de Consulta...")
        
        try:
            response = self.session.get(self.guia_consulta_url)
            response.raise_for_status()
            self.salvar_html_para_debug(response.text, "pagina_guia_consulta")
            
            if "Guia de Consulta" in response.text:
                print("Página de Guia de Consulta acessada com sucesso!")
                return response.text
            else:
                print("Não foi possível acessar a página de Guia de Consulta.")
                # Verificar se foi redirecionado para a página de login
                if "login" in response.url.lower():
                    print("Fomos redirecionados para a página de login. A sessão pode ter expirado.")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar a página de Guia de Consulta: {e}")
            return None

    def buscar_paciente(self, html_guia_consulta):
        """Busca o paciente pelo número da carteira"""
        print(f"Buscando paciente com carteira: {self.numero_carteira}...")
        
        if not html_guia_consulta:
            print("HTML da página de Guia de Consulta não disponível.")
            return False
        
        # Processar a página de busca
        soup = BeautifulSoup(html_guia_consulta, 'html5lib')
        
        # Salvar a página para debug
        self.salvar_html_para_debug(html_guia_consulta, "pagina_busca_paciente")
        
        # Procurar formulário de busca
        search_form = None
        forms = soup.find_all('form')
        
        for form in forms:
            # Procurar por campo de busca de carteira/paciente
            carteira_field = form.find('input', {'name': re.compile(r'(carteira|numero|paciente)', re.I)})
            if carteira_field:
                search_form = form
                print(f"Formulário de busca encontrado. Campo de carteira: {carteira_field.get('name')}")
                break
        
        if not search_form:
            print("Não foi possível encontrar o formulário de busca.")
            return False
        
        # Extrair action do formulário
        form_action = search_form.get('action')
        if not form_action or form_action == '#':
            form_action = self.guia_consulta_url
        elif not form_action.startswith('http'):
            # Completar URL relativa
            if form_action.startswith('/'):
                form_action = f"https://saude.sulamericaseguros.com.br{form_action}"
            else:
                form_action = f"{self.guia_consulta_url.rstrip('/')}/{form_action.lstrip('/')}"
        
        print(f"URL de busca: {form_action}")
        
        # Extrair campos do formulário
        carteira_field_name = None
        for input_field in search_form.find_all('input'):
            if re.search(r'(carteira|numero|paciente)', input_field.get('name', ''), re.I):
                carteira_field_name = input_field.get('name')
                break
        
        if not carteira_field_name:
            print("Não foi possível identificar o campo para número de carteira.")
            carteira_field_name = "numero_carteira"  # Valor padrão como fallback
        
        # Extrair inputs hidden
        hidden_values = {}
        for hidden in search_form.find_all('input', {'type': 'hidden'}):
            if hidden.get('name'):
                hidden_values[hidden.get('name')] = hidden.get('value', '')
        
        # Preparar dados para a busca
        search_data = hidden_values.copy()
        search_data[carteira_field_name] = self.numero_carteira
        
        # Identificar botão de submit
        submit_button = search_form.find('button', {'type': 'submit'}) or search_form.find('input', {'type': 'submit'})
        if submit_button and submit_button.get('name'):
            search_data[submit_button.get('name')] = submit_button.get('value', '')
        
        print(f"Dados de busca: {json.dumps({k: v for k, v in search_data.items() if k == carteira_field_name}, indent=2)}")
        
        # Enviar a busca
        try:
            search_response = self.session.post(
                form_action,
                data=search_data,
                headers={
                    "Referer": self.guia_consulta_url,
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
            search_response.raise_for_status()
            
            # Salvar a resposta para análise
            self.salvar_html_para_debug(search_response.text, "resposta_busca_paciente")
            
            # Processar resultado
            result_soup = BeautifulSoup(search_response.text, 'html5lib')
            
            # Verificar se há resultados
            # Procurar por divs com informações do paciente ou tabelas de resultado
            result_elements = result_soup.find_all(['div', 'table'], {'class': re.compile(r'(resultado|paciente|info)', re.I)})
            
            if result_elements:
                print("Resultados da busca encontrados:")
                for element in result_elements:
                    print(f"  {element.get_text(strip=True, separator=' | ')}")
                return True
            else:
                print("Nenhum resultado encontrado na busca.")
                # Verificar mensagens de erro ou "não encontrado"
                error_messages = result_soup.find_all(['div', 'span', 'p'], {'class': re.compile(r'(alert|error|msg-erro|not-found)', re.I)})
                for error in error_messages:
                    print(f"  Mensagem: {error.get_text(strip=True)}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"Erro ao enviar busca: {e}")
            return False

    def executar_automacao(self):
        """Executa o fluxo completo de automação"""
        print("Iniciando automação de login e busca de paciente...")
        
        # Etapa 1: Login
        if not self.login():
            print("Falha no login. Encerrando automação.")
            return False
        
        # Aguardar um momento para garantir que a sessão está estabelecida
        print("Aguardando 3 segundos para estabilizar a sessão...")
        time.sleep(3)
        
        # Antes de acessar a guia, vamos verificar se já temos uma sessão válida
        print("Verificando se temos uma sessão válida...")
        try:
            home_page = self.session.get("https://saude.sulamericaseguros.com.br/prestador/home/")
            self.salvar_html_para_debug(home_page.text, "pagina_home_apos_login")
            
            if "login" in home_page.url.lower():
                print("Fomos redirecionados para login novamente. A sessão não está válida.")
                print("Tentando um segundo login...")
                if not self.login():
                    print("Segunda tentativa de login falhou. Encerrando automação.")
                    return False
                print("Aguardando após segunda tentativa de login...")
                time.sleep(3)
        except Exception as e:
            print(f"Erro ao verificar sessão: {e}")
        
        # Etapa 2: Acessar Guia de Consulta
        print("Tentando acessar a guia de consulta...")
        html_guia = self.acessar_guia_consulta()
        if not html_guia:
            print("Falha ao acessar a página de Guia de Consulta.")
            
            # Tentar acessar pelo caminho alternativo
            print("Tentando acessar por caminho alternativo...")
            try:
                alt_url = "https://saude.sulamericaseguros.com.br/prestador/servicos-medicos/"
                resp = self.session.get(alt_url)
                self.salvar_html_para_debug(resp.text, "pagina_servicos_medicos")
                
                soup = BeautifulSoup(resp.text, 'html5lib')
                links = soup.find_all('a')
                
                guia_links = []
                for link in links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    if 'consulta' in href.lower() or 'consulta' in text.lower():
                        guia_links.append((text, href))
                
                if guia_links:
                    print(f"Encontrados {len(guia_links)} links possíveis para Guia de Consulta:")
                    for i, (text, href) in enumerate(guia_links):
                        print(f"  {i+1}. {text}: {href}")
                    
                    # Tentar o primeiro link
                    if guia_links:
                        first_link = guia_links[0][1]
                        if not first_link.startswith('http'):
                            if first_link.startswith('/'):
                                first_link = f"https://saude.sulamericaseguros.com.br{first_link}"
                            else:
                                first_link = f"https://saude.sulamericaseguros.com.br/{first_link}"
                        
                        print(f"Tentando acessar: {first_link}")
                        alt_resp = self.session.get(first_link)
                        self.salvar_html_para_debug(alt_resp.text, "pagina_link_alternativo")
                        
                        if "consulta" in alt_resp.text.lower():
                            print("Página alternativa acessada com sucesso!")
                            html_guia = alt_resp.text
                        else:
                            print("Página alternativa não parece ser a guia de consulta.")
                
            except Exception as e:
                print(f"Erro ao tentar caminho alternativo: {e}")
            
            if not html_guia:
                print("Todas as tentativas de acessar a guia de consulta falharam. Encerrando automação.")
                return False
        
        # Aguardar um momento para que a página seja completamente carregada
        print("Aguardando 2 segundos para garantir carregamento completo...")
        time.sleep(2)
        
        # Etapa 3: Buscar Paciente
        resultado_busca = self.buscar_paciente(html_guia)
        
        if resultado_busca:
            print("Automação concluída com sucesso!")
            return True
        else:
            print("Falha na busca do paciente. Automação concluída com erros.")
            return False


# Executar o script
if __name__ == "__main__":
    automacao = SulAmericaAutomacao()
    automacao.executar_automacao()