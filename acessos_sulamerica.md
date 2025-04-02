### Automacao de Login e Busca de Paciente via Requests (Python)

#### Objetivo:
Automatizar o processo de login na plataforma e localizar um paciente utilizando a carteira de saúde fornecida.

#### Etapas do Processo:
1. **Login na Plataforma**
   - Utilizar as credenciais fornecidas:
     - Usuário: `master`
     - Senha: `837543`
     - Código de Identificação: `100000009361`
   - Realizar a autenticação via requisição HTTP utilizando a biblioteca `requests` em Python.
   
2. **Navegação até a Página de Busca de Pacientes**
   - Acessar o menu: `Serviços Médicos > Faturamento > Guia de Consulta`
   
3. **Busca do Paciente**
   - Localizar o paciente utilizando o número da carteira: `55788888485177660015`
   - Realizar a consulta na API ou via scraping da interface da plataforma, conforme necessário.

#### Observação Importante:
- As credenciais são individuais para cada candidato. Caso ocorra qualquer problema, será possível rastrear a atividade realizada com cada login.
- **Todas as interações devem ser feitas exclusivamente usando `requests`. Não é permitido o uso de Selenium ou qualquer outra plataforma que utilize WebDriver.**

