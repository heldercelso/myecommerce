## Introdução

Este ecommerce foi desenvolvido majoritariamente em Django com banco de dados PostgreSQL e tem como objetivo
cobrir todas as funcionalidades básicas de um comércio eletrônico desde login e cadastro de usuários até o
pagamento dos produtos.


## Tecnologias

A implementação foi realizada utilizando Python na versão 3.7 tendo como bibliotecas principais as seguintes:

 - django
 - mercadopago
 - pytest
 - coverage

Outras linguagens/tecnologias utilizadas:

 - Front-end: Javascript/HTML/CSS
 - Docker

### Estrutura

```shell
.
├── conftest.py                                                           # arquivo de fixture para o pytest
├── docker_entrypoint.sh                                                  # Entrypoint para o docker
├── docker-compose.yaml                                                   # docker-compose
├── environment.env                                                       # variáveis de ambiente para o docker-compose
├── Dockerfile                                                            # Arquivo de deploy
├── pytest.ini                                                            # arquivo de setup do pytest
├── README.md
├── requirements.txt                                                      # bibliotecas
├── ecommerce                                                             # projeto do django
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── main_app                                                              # aplicação django principal
│   ├── templatetags
│   │   └── cart_template_tags.py
│   ├── tests
│   │   ├── factories.py
│   │   ├── test_cart.py
│   │   ├── test_models.py
│   │   ├── test_views.py
│   │   └── tests.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
├── media_root                                                            # armazenando das imagens
├── mercadopago_payment                                                   # aplicação django para o pagamento (mercadopago)
│   ├── tests
│   │   ├── factories.py
│   │   ├── test_forms.py
│   │   ├── test_models.py
│   │   └── test_views.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── middleware.py
│   ├── models.py
│   ├── urls.py
│   ├── utils.py
│   └── views.py
├── postgres_data                                                         # banco de dados
├── static                                                                # armazenando dos arquivos estáticos (css/js/...)
└── templates                                                             # armazenando do front-end (html)
```


## Executando o projeto:

Para executar o projeto é necessário ter instalado em seu ambiente `docker` e `docker-compose`. Mas antes é necessário preencher o arquivo environment.env na raiz do projeto.



```shell
# Para buildar e executar, use o comando:
$ docker-compose up

# Apenas buildar, execute:
$ docker-compose build

# Para desativar:
$ docker-compose down
```

A partir desse ponto todos os containers estarão disponíveis.
Para acessar a aplicação basta abrir em seu navegador o endereço `http://localhost:8000`.

### Lidando com o projeto

Para adicionar produtos a loja:

1. Crie um superuser:
```shell
# Criar superuser (admin), execute o comando e preencha nome de usuário, email e senha:
$ docker exec -ti web createsuperuser
```
2. Abra o navegador e acesse `localhost:8000/admin`, em seguida faça login com o usuário criado anteriormente.

3. Já logado no painel de admin, vá em Produtos e preencha os campos.


### Configurando MercadoPago

 1. Criar conta MercadoPago: https://www.mercadopago.com.br/developers
 2. Criar chaves de teste em: https://www.mercadopago.com.br/developers/panel/credentials
 2. Copiar chaves e preencher no environment.env: MERCADO_PAGO_PUBLIC_KEY e MERCADO_PAGO_ACCESS_TOKEN

OBS: Para colocar o Mercadopago pagamentos em produção ative as credenciais de produção no mesmo link mencionado acima e use as chaves.


## Desenvolvimento

A estrutura contida no arquivo `docker-compose.yaml` fornece containers distintos para o projeto Django e o banco de dados.

### Banco de dados

Todas as alterações relacionadas ao banco de dados devem ser feitas utilizando o ORM do próprio Django. Para criar uma nova migração basta executar o comando `docker exec -ti web python manage.py makemigrations` e `docker exec -ti web python manage.py migrate`.

### Testes

Para executar os testes basta inserir os seguintes comandos no seu terminal:

```shell
# Executa os testes com coverage para gerar o relatório de cobertura:
$ docker exec -ti web coverage run -m pytest -vx

# Exibe o relatório e lista as linhas que não estão cobertas pelos testes:
$ docker exec -ti web coverage report -i
```

Atualmente esse projeto contém uma cobertura de testes de 70%.

### Melhorias que podem ser feitas

- Adicionar cálculo do frete e prazo de entrega;
- Adicionar outros meios de pagamento:
   https://www.mercadopago.com.br/developers/pt/docs/checkout-api/payment-methods/other-payment-methods
- Salvar e obter cartões do usuário no mercadopago;
- Traduzir Front-end.