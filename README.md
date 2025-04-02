# Automação Portal SulAmérica

Script para automatizar o login e busca de beneficiários no portal da SulAmérica Seguros.

## Requisitos

- Python 3.6+
- Pacote `requests`

## Instalação

1. Clone o repositório ou baixe o arquivo `sulamerica_automation.py`

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Uso

Execute o script com Python:

```bash
python3 sulamerica_automation.py
```

## Configuração

O script está configurado com as seguintes credenciais por padrão:

- **Usuário**: master
- **Senha**: 837543
- **Código de Identificação**: 100000009361

E busca o beneficiário com código: 55788888485177660015

Para alterar essas informações, edite as variáveis no método `main()` do arquivo `sulamerica_automation.py`:

```python
username = "master"                  # Altere para seu usuário
password = "837543"                  # Altere para sua senha
identification_code = "100000009361" # Altere para seu código de identificação
beneficiary_code = "55788888485177660015" # Altere para o código do beneficiário
```

## Funcionalidades

- Realiza login no portal SulAmérica
- Navegação automática até a página de busca de pacientes
- Busca paciente pelo número da carteira
- Tratamento automático de sessão expirada

## Logs

Os logs são exibidos no console, mostrando o progresso da automação. 
