## Introduction

This ecommerce was developed mostly in Django with PostgreSQL database and aims to
cover all the basic functionalities of an e-commerce from login and user registration to the
payment of the products.

Project images: https://helder-portfolio.herokuapp.com/ecommerce-1/


## Technologies

The implementation was carried out using Python version 3.7 with the following main libraries:

 - django
 - mercadopago
 - pytest
 - coverage

Other languages/technologies used:

 - Front-end: Javascript/HTML/CSS
 - Docker

### Structure

```shell
.
├── ecommerce                                                             # django project
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── main_app                                                              # main django application
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
├── media_root                                                            # product image storage
├── mercadopago_payment                                                   # django application for payments (mercadopago)
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
├── postgres_data                                                         # database
├── static                                                                # static file storage (css/js/...)
├── templates                                                             # front-end storage (html)
├── conftest.py                                                           # pytest fixture file
├── docker-compose.yaml                                                   # docker-compose
├── docker_entrypoint.sh                                                  # docker Entrypoint
├── Dockerfile                                                            # docker build file
├── environment.env                                                       # environment variables
├── manage.py
├── pytest.ini                                                            # pytest setup
├── README.md
└── requirements.txt                                                      # libraries
```


## Running the project

To run the project it is necessary to have `docker` and `docker-compose` installed in your environment. But first it is necessary to fill the environment.env file in the project root.

```shell
# Command to build and execute:
$ docker-compose up

# Only build:
$ docker-compose build

# Turn-off command:
$ docker-compose down
```

From that point on, all containers will be available.
To access the application, just open the address `http://localhost:8000` in your browser.

### Handling the project

To add products to the store:

1. Create a superuser:
```shell
# Create superuser (admin), run the command and fill username, email and password:
$ docker exec -ti web createsuperuser
```

2. Open the browser and go to `localhost:8000/admin`, then login with the user created earlier.

3. Once logged into the admin panel, go to Products and fill in the fields.

### Configuring MercadoPago

 1. Create a MercadoPago account: https://www.mercadopago.com.br/developers
 2. Create test keys at: https://www.mercadopago.com.br/developers/panel/credentials
 2. Copy keys and fill in the environment.env: `MERCADO_PAGO_PUBLIC_KEY` and `MERCADO_PAGO_ACCESS_TOKEN`

NOTE: To put Mercadopago into production, activate the production credentials in the same link mentioned above and use the keys.


## Development

The structure contained in the `docker-compose.yaml` file provides separate containers for the Django project and the database (PostgreSQL).

### Database

All database-related changes must be made using Django's own ORM. To create a new migration just run `docker exec -ti web python manage.py makemigrations` and `docker exec -ti web python manage.py migrate`.
The model diagram can be seen in the root directory of this project as `database_diagram.png`.

Command to generate database diagram (it needs django-extensions and pygraphviz libs):
```shell
$ docker exec -ti web python manage.py graph_models main_app mercadopago_payment -g -o database_diagram.png
```

## Tests

To run the tests, simply enter the following commands in your terminal:

```shell
# Run the tests with coverage to generate the coverage report:
$ docker exec -ti web coverage run -m pytest -vx

# Display the report and list the lines that are not covered by the tests:
$ docker exec -ti web coverage report -i
```

To validate templates:
```shell
$ docker exec -ti web python manage.py validate_templates
```

This project currently contains 70% of test coverage.

## Improvements that can be made

- Add freight calculation and delivery time;
- Add other payment methods:
   https://www.mercadopago.com.br/developers/pt/docs/checkout-api/payment-methods/other-payment-methods
- Save and get user credit-cards on MercadoPago;
- Translate Front-end.
