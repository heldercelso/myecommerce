// MercadoPago implementation:
// - https://www.mercadopago.com.br/developers/pt/guides/online-payments/checkout-api/receiving-payment-by-card
// References:
// - https://github.com/mercadopago/sdk-js

// reload button reload the current page on click - used for errors
$("#button-reload").click(function() {
  sessionStorage.setItem("reloading", "true");
  window.location.reload();
});

// Applying mask to cardnumber and doc_number fields
$('input[id="form-checkout__cardNumber"]').mask('0000 0000 0000 0000');
$('input[id="form-checkout__identificationNumber"]').mask('000.000.000-00');
$('input[id="form-checkout__expirationDate"]').mask('00/0000');


// Removing mask to submit
$("#form-checkout").submit(function() {
    $("#form-checkout__cardNumber").unmask();
    $("#form-checkout__identificationNumber").unmask();
    $('#form-checkout__submit').attr('disabled', true);
    $('#form-checkout input').prop("disabled", true);
    $('#form-checkout select').prop("disabled", true);
});

// resolving client-side issues messages of incorrect data
function get_error_message(code_or_message) {
    // console.log('Error code: ', error_code);
    messages = {
       // messages of incorrect client data
      '000': 'Parâmetros inválidos.',
      '205': 'Digite o número do seu cartão.', // 'parameter cardNumber can not be null/empty'
      '208': 'Escolha um mês.', // 'parameter cardExpirationMonth can not be null/empty'
      '209': 'Escolha um ano.', // 'parameter cardExpirationYear can not be null/empty'
      '212': 'Informe seu documento.', // 'parameter docType can not be null/empty'
      '213': 'Informe seu documento.', // 'The parameter cardholder.document.subtype can not be null or empty'
      '214': 'Informe seu documento.', // 'parameter docNumber can not be null/empty'
      '220': 'Informe seu banco emissor.', // 'parameter cardIssuerId can not be null/empty'
      '221': 'Digite o nome e sobrenome.', // 'parameter cardholderName can not be null/empty'
      '224': 'Digite o código de segurança.', // 'parameter securityCode can not be null/empty'
      'E203': 'Confira o código de segurança.', // 'invalid parameter securityCode'
      'E301': 'Há algo de errado com esse número. Digite novamente.', // 'invalid parameter cardNumber'
      'E302': 'Código de segurança inválido.',
      '316': 'Por favor, digite um nome válido.', // 'invalid parameter cardholderName'
      '322': 'Confira seu documento.', // 'invalid parameter docType'
      '323': 'Confira seu documento.', // 'invalid parameter cardholder.document.subtype'
      '324': 'Confira seu documento.', // 'invalid parameter docNumber'
      '325': 'Confira a data.', // 'invalid parameter cardExpirationMonth'
      '326': 'Confira a data.', // 'invalid parameter cardExpirationYear'

       // uncommon client-side issues messages of incorrect data
      'El bin \'0\' no puede tener menos de 6 dígitos': 'Sequência de digítos inválida.',
      'invalid expiration_year': 'Ano de vencimento inválido.',
      'an error occurred doing POST card_token': 'Erro no processamento com o servidor da pagadora. Confira os dados e tente novamente.',
    
       // client-side issues messages on token creation
      '106': 'Não pode efetuar pagamentos a usuários de outros países.', // Cannot operate between users from different countries
      '109': 'O payment_method_id não processa pagamentos parcelados. Escolha outro cartão ou outra forma de pagamento.', // Invalid number of shares for this payment_method_id
      '126': 'Não conseguimos processar seu pagamento.', // The action requested is not valid for the current payment state
      '129': 'O payment_method_id não processa pagamentos para o valor selecionado. Escolha outro cartão ou outra forma de pagamento.', // Cannot pay this amount with this paymentMethod
      '145': 'Uma das partes com a qual está tentando realizar o pagamento é um usuário de teste e a outra é um usuário real.', // Invalid users involved
      '150': 'Você não pode efetuar pagamentos.', // The payer_id cannot do payments currently
      '151': 'Você não pode efetuar pagamentos.', // The payer_id cannot do payments with this payment_method_id
      '160': 'Não conseguimos processar seu pagamento.', // Collector not allowed to operate
      '204': 'O payment_method_id não está disponível nesse momento. Escolha outro cartão ou outra forma de pagamento.', // Unavailable payment_method
      '801': 'Você realizou um pagamento similar há poucos instantes. Tente novamente em alguns minutos.', // Already posted the same request in the last minute
    }
    if (code_or_message in messages) {
      return messages[code_or_message]
    } else {
      return 'Pagamento não realizado! Algum erro desconhecido ocorreu. Confira os dados e tente novamente.'
    }
}


// getting message errors
function show_error(error, error_type) {
  if (error) {

    if ("message" in error) {
      error_msg = get_error_message(error["message"]);
    } else if (error && "code" in error[0]) {
        error_msg = get_error_message(error[0]["code"]);
    }

    document.getElementById("error-message").style.display = "block";
    document.getElementById("error-message").innerText = error_msg;

    $('#form-checkout__submit').prop("disabled", false);
    $('#form-checkout input').prop("disabled", false);
    $('#form-checkout select').prop("disabled", false);

    // $('input[id="form-checkout__cardNumber-container"]').mask('0000 0000 0000 0000');
    // $('input[id="form-checkout__identificationNumber"]').mask('000.000.000-00');
    // $('input[id="form-checkout__expirationDate-container"]').mask('00/0000');
    return console.warn(error_type, error);
  }
  return false;
}

const cardForm = mp.cardForm({
    amount: document.getElementById('transaction_amount').value,
    autoMount: true,
    processingMode: 'aggregator',
    form: {
        id: 'form-checkout',
        cardholderName: {
            id: 'form-checkout__cardholderName',
            // placeholder: 'Cardholder name',
            placeholder: 'Titular do cartão',
        },
        cardholderEmail: {
            id: 'form-checkout__cardholderEmail',
            placeholder: 'Email',
        },
        cardNumber: {
            id: 'form-checkout__cardNumber',
            // placeholder: 'Card number',
            placeholder: 'Número do cartão',
        },
        expirationDate: {
            id: 'form-checkout__expirationDate',
            placeholder: 'MM/YYYY'
        },
        securityCode: {
            id: 'form-checkout__securityCode',
            placeholder: 'CVV',
        },
        installments: {
            id: 'form-checkout__installments',
            // placeholder: 'Total installments'
            placeholder: 'Parcelas'
        },
        identificationType: {
            id: 'form-checkout__identificationType',
            // placeholder: 'Document type'
            placeholder: 'Tipo de documento'
        },
        identificationNumber: {
            id: 'form-checkout__identificationNumber',
            // placeholder: 'Document number'
            placeholder: 'Número do documento'
        },
        issuer: {
            id: 'form-checkout__issuer',
            // placeholder: 'Issuer'
            placeholder: 'Banco emissor'
        }
    },
    callbacks: {
        onFormMounted: error => {
          if (show_error(error, "Form Mounted handling errorr: ") == false) {
            console.log("Form mounted");
          }
        },
        onFormUnmounted: error => {
          if (show_error(error, "Form Unmounted handling error: ") == false) {
            console.log('Form unmounted');
          }
        },
        onIdentificationTypesReceived: (error, identificationTypes) => {
          if (show_error(error, "identificationTypes handling error: ") == false) {
            console.log('Identification types available: ', identificationTypes);
          }
        },
        onPaymentMethodsReceived: (error, paymentMethods) => {
          if (show_error(error, "paymentMethods handling error: ") == false) {
            console.log('Payment Methods available: ', paymentMethods)
          }
        },
        onIssuersReceived: (error, issuers) => {
          if (show_error(error, "issuers handling error: ") == false) {
            console.log('Issuers available: ', issuers);
          }
        },
        onInstallmentsReceived: (error, installments) => {
          if (show_error(error, "issuers handling error: ") == false) {
            console.log('Installments available: ', installments);
          }
        },
        onCardTokenReceived: (error, token) => {
          console.log("Mercadopago error on token generation", error);
          if (show_error(error, "Token handling error: ") == false) {
            console.log('Token created.');
            console.log('Token available: ', token);
          }
        },
        onSubmit: event => {
            event.preventDefault();

            document.getElementById("error-message").style.display = "none";
            document.getElementById("error-message").innerText = '';

            // const cardData = cardForm.getCardFormData();
            const {
                paymentMethodId: payment_method_id,
                issuerId: issuer_id,
                cardholderEmail: email,
                amount,
                token,
                installments,
                identificationNumber,
                identificationType
            } = cardForm.getCardFormData();

            fetch("/payments/process/", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json;',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    token,
                    issuer_id,
                    email,
                    payment_method_id,
                    card_holder: document.getElementById('form-checkout__cardholderName').value,
                    transaction_amount: Number(amount),
                    installments: Number(installments),
                    // description: "Ecommerce products",
                    type: identificationType,
                    number: identificationNumber,
                }),
            })
            .then(function(value) { // Promise
                return value.json();
            })
            .then(function(json_data) { // Content
                const json_errors = json_data["errors"];
                for (key_error in json_errors) {
                    for (error in json_errors[key_error]) {
                        document.getElementById("error-message").style.display = "block";
                        document.getElementById("error-message").innerText += json_errors[key_error][error]["message"] + '\n';
                        document.getElementById("button-reload").style.display = "block";
                    }
                }

                if (json_data["redirect_url"] && json_data["redirect_url"] != window.location.pathname) {
                    redirect_url = window.location.protocol + "//" + window.location.host + json_data["redirect_url"];
                    window.location.href = redirect_url;
                }

            })
            .catch(error => {
                console.log(error);
                // console.log("Unexpected error\n"+JSON.stringify(error));
            });
        },
        onFetching:(resource) => {
            console.log('Fetching resource: ', resource)

            // Animate progress bar
            const progressBar = document.querySelector('.progress-bar')
            progressBar.removeAttribute('value')

            return () => {
                progressBar.setAttribute('value', '0')
            }
        },
        onError: (error, event) => {
            console.log(event, error);
        },
        onValidityChange: (error, field) => {
            if (error) return error.forEach(e => console.log(`${field}: ${e.message}`));
            console.log(`${field} is valid`);
        },
        onReady: () => {
            console.log("CardForm ready");
        }
    }
})