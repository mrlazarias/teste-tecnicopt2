# Automação Portal SulAmérica

Script para automatizar o login e busca de beneficiários no portal da SulAmérica Seguros.

## Requisitos

- Python 3.6+
- Bibliotecas necessárias: `requests`, `beautifulsoup4`, `html5lib`

## Instalação

1. Clone o repositório ou baixe o arquivo `automacao_sulamerica.py`

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Configuração

As credenciais de acesso e o número da carteira do paciente estão configurados no início da classe `SulAmericaAutomacao`:

```python
# Credenciais de acesso
self.usuario = "master"
self.senha = "837543"
self.codigo_referenciado = "100000009361"

# Número da carteira do paciente
self.numero_carteira = "55788888485177660015"
```

Modifique estas informações conforme necessário para suas credenciais e o paciente que deseja consultar.

## Uso

Execute o script com Python:

```bash
python automacao_sulamerica.py
```

O script irá:

1. Realizar login no portal SulAmérica
2. Acessar a página de Guia de Consulta
3. Buscar o paciente pelo número da carteira
4. Salvar os resultados em arquivos HTML para análise

## Arquivos de Debug

Durante a execução, o script gera vários arquivos HTML para ajudar na depuração e compreensão do processo:

- `pagina_login.html` - Página de login inicial
- `pagina_apos_login.html` - Página após o login
- `pagina_home_apos_login.html` - Página inicial após login
- `pagina_guia_consulta.html` - Página de Guia de Consulta (se acessada)
- `pagina_busca_paciente.html` - Página de busca de paciente
- `resposta_busca_paciente.html` - Resposta da busca

## Problemas Conhecidos

O portal SulAmérica possui mecanismos de segurança que podem impedir o acesso direto a páginas restritas via scripts. Alguns problemas comuns:

1. **Sessão expirando rapidamente**: O script tenta lidar com isso fazendo um segundo login se necessário.

2. **Redirecionamento para a página de login**: Quando tentamos acessar páginas protegidas, o portal pode redirecionar para a página de login.

3. **Estrutura da página pode mudar**: O script utiliza análise da estrutura do HTML para localizar formulários e campos, que podem ser alterados pelo SulAmérica.

## Recomendações

Se você estiver enfrentando problemas com o script, considere as seguintes alternativas:

1. **Usar Selenium ou Playwright**: Estas ferramentas simulam um navegador real, o que pode ser mais eficaz contra medidas anti-scraping.

2. **Adicionar mais atrasos**: Aumentar os tempos de espera entre as ações pode ajudar a evitar detecção.

3. **Usar cookies de uma sessão manual**: Você pode fazer login manualmente, exportar os cookies e usá-los no script.

4. **Solicitar API oficial**: Se este uso for para fins comerciais legítimos, considere entrar em contato com a SulAmérica para verificar se eles oferecem uma API oficial ou método de integração.

## Personalização

O script foi projetado para ser facilmente entendido e modificado. Se você precisar fazer alterações:

- Modifique as URLs em `__init__` se os endereços mudarem
- Ajuste os tempos de espera em `time.sleep()` conforme necessário
- Adicione tratamento para outros tipos de formulários ou layout do site

