import random
import string
import uuid
from decimal import Decimal
import json

def create_ref_code():
    """ Return a unique ID to represent the order """
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))

def create_unique_ref_code():
    return str(uuid.uuid4())

class DecimalEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Decimal):
      return str(obj)
    return json.JSONEncoder.default(self, obj)

""" Mercadopago error messages """
def rejected_error_msg(status_detail):
    if status_detail == 'cc_rejected_bad_filled_card_number':
        return 'Revise o número do cartão.'
    elif status_detail == 'cc_rejected_bad_filled_date':
        return 'Revise a data de vencimento.'
    elif status_detail == 'cc_rejected_bad_filled_other':
        return 'Revise os dados.'
    elif status_detail == 'cc_rejected_bad_filled_security_code':
        return 'Revise o código de segurança do cartão.'
    elif status_detail == 'cc_rejected_blacklist':
        return 'Não pudemos processar seu pagamento.'
    elif status_detail == 'cc_rejected_call_for_authorize':
        return 'Você deve autorizar o pagamento do valor ao Mercado Pago.'
    elif status_detail == 'cc_rejected_card_disabled':
        return 'Ligue para sua operadora para ativar seu cartão. O telefone está no verso do seu cartão.'
    elif status_detail == 'cc_rejected_card_error':
        return 'Não conseguimos processar seu pagamento.'
    elif status_detail == 'cc_rejected_duplicated_payment':
        return 'Você já efetuou um pagamento com esse valor. Caso precise pagar novamente, utilize outro cartão ou outra forma de pagamento.'
    elif status_detail == 'cc_rejected_high_risk':
        return 'Seu pagamento foi recusado.'
    elif status_detail == 'cc_rejected_insufficient_amount':
        return 'Saldo insuficiente.'
    elif status_detail == 'cc_rejected_invalid_installments':
        return 'Sua operadora do cartão não processa pagamentos em parcelas.'
    elif status_detail == 'cc_rejected_max_attempts':
        return 'Você atingiu o limite de tentativas permitido.'
    elif status_detail == 'cc_rejected_other_reason':
        return 'Sua operadora não processou o pagamento.'
    elif status_detail == 'cc_rejected_card_type_not_allowed':
        return 'O pagamento foi rejeitado porque o usuário não tem a função crédito habilitada em seu cartão multiplo (débito e crédito).'
    return 'Aconteceu algum erro inesperado. Verifique os dados e tente novamente.'

def error_msg(code):
    if code == 1:
        return 'Erro de parâmetros.'
    elif code == 3:
        return 'O token deve ser para teste.'
    elif code == 5:
        return 'Deve fornecer seu access_token para continuar.'
    elif code == 23:
        return "Os parâmetros a seguir devem ter data e formato válidos (aaaa-MM-dd'T'HH:mm:ssz) date_of_expiration."
    elif code == 1000:
        return 'O número de linhas excedeu os limites.'
    elif code == 1001:
        return "O formato de data deve ser aaaa-MM-dd'T'HH:mm:ss.SSSZ."
    elif code == 2001:
        return 'Já postei o mesmo pedido no último minuto.'
    elif code == 2002:
        return 'Cliente não encontrado.'
    elif code == 2004:
        return 'Falha no POST para a API de Transações do Gateway.'
    elif code == 2006:
        return 'Cartão Token não encontrado.'
    elif code == 2007:
        return 'Falha na conexão com a API Card Token.'
    elif code == 2009:
        return 'O emissor do token do cartão não pode ser nulo.'
    elif code == 2060:
        return 'O cliente não pode ser igual ao cobrador.'
    elif code == 3000:
        return 'Você deve fornecer o nome do titular do cartão com os dados do seu cartão.'
    elif code == 3001:
        return 'Você deve fornecer seu cardissuer_id com os dados do seu cartão.'
    elif code == 3003:
        return 'Card_token_id inválido.'
    elif code == 3004:
        return 'Parâmetro inválido site_id.'
    elif code == 3005:
        return 'Ação inválida, o recurso está em um estado que não permite esta operação. Para obter mais informações, consulte o estado que possui o recurso.'
    elif code == 3006:
        return 'Parâmetro inválido cardtoken_id.'
    elif code == 3007:
        return 'O parâmetro client_id não pode ser nulo ou vazio.'
    elif code == 3008:
        return 'Cartão não encontrado.'
    elif code == 3009:
        return 'client_id não autorizado.'
    elif code == 3010:
        return 'Cartão não encontrado na lista de permissões.'
    elif code == 3011:
        return 'Não encontrado payment_method.'
    elif code == 3012:
        return 'Parâmetro inválido security_code_length.'
    elif code == 3013:
        return 'O parâmetro security_code é um campo obrigatório não pode ser nulo ou vazio.'
    elif code == 3014:
        return 'Parâmetro inválido payment_method.'
    elif code == 3015:
        return 'Parâmetro inválido card_number_length.'
    elif code == 3016:
        return 'Parâmetro inválido card_number.'
    elif code == 3017:
        return 'O parâmetro card_number_id não pode ser nulo ou vazio.'
    elif code == 3018:
        return 'O parâmetro expire_month não pode ser nulo ou vazio.'
    elif code == 3019:
        return 'O parâmetro expire_year não pode ser nulo ou vazio.'
    elif code == 3020:
        return 'O parâmetro cardholder.name não pode ser nulo ou vazio.'
    elif code == 3021:
        return 'O parâmetro cardholder.document.number não pode ser nulo ou vazio.'
    elif code == 3022:
        return 'O parâmetro cardholder.document.type não pode ser nulo ou vazio.'
    elif code == 3023:
        return 'O parâmetro cardholder.document.subtype não pode ser nulo ou vazio.'
    elif code == 3024:
        return 'Ação inválida - reembolso parcial não suportado para esta transação.'
    elif code == 3025:
        return 'Código de autenticação inválido.'
    elif code == 3026:
        return 'Card_id inválido para este payment_method_id.'
    elif code == 3027:
        return 'Payment_type_id inválido.'
    elif code == 3028:
        return 'Payment_method_id inválido.'
    elif code == 3029:
        return 'Mês de expiração do cartão inválido.'
    elif code == 3030:
        return 'Ano de expiração do cartão inválido.'
    elif code == 3034: #Invalid card_number_validation
        return 'Validação do Número de cartão falhou. Verifique os dígitos e tente novamente.'
    elif code == 4000:
        return 'o atributo do cartão não pode ser nulo.'
    elif code == 4001:
        return 'O atributo payment_method_id não pode ser nulo.'
    elif code == 4002:
        return 'O atributo transaction_amount não pode ser nulo.'
    elif code == 4003:
        return 'O atributo transaction_amount deve ser numérico.'
    elif code == 4004:
        return 'o atributo de parcelas não pode ser nulo.'
    elif code == 4005:
        return 'o atributo de parcelas deve ser numérico.'
    elif code == 4006:
        return 'o atributo do pagador está malformado.'
    elif code == 4007:
        return 'O atributo site_id não pode ser nulo.'
    elif code == 4012:
        return 'O atributo payer.id não pode ser nulo.'
    elif code == 4013:
        return 'O atributo payer.type não pode ser nulo.'
    elif code == 4015:
        return 'O atributo payment_method_reference_id não pode ser nulo.'
    elif code == 4016:
        return 'O atributo payment_method_reference_id deve ser numérico.'
    elif code == 4017:
        return 'atributo de status não pode ser nulo.'
    elif code == 4018:
        return 'O atributo payment_id não pode ser nulo.'
    elif code == 4019:
        return 'O atributo payment_id deve ser numérico.'
    elif code == 4020:
        return 'O atributo notelification_url deve ser url válido.'
    elif code == 4021:
        return 'O atributo notelification_url deve ter menos de 500 caracteres.'
    elif code == 4022:
        return 'O atributo de metadados deve ser um JSON válido.'
    elif code == 4023:
        return 'O atributo transaction_amount não pode ser nulo.'
    elif code == 4024:
        return 'O atributo transaction_amount deve ser numérico.'
    elif code == 4025:
        return 'refund_id não pode ser nulo.'
    elif code == 4026:
        return 'Cupom_amount inválido.'
    elif code == 4027:
        return 'O atributo Campaign_id deve ser numérico.'
    elif code == 4028:
        return 'O atributo de valor_cupom deve ser numérico.'
    elif code == 4029:
        return 'Tipo de pagador inválido.'
    elif code == 4037:
        return 'Transaction_amount inválida.'
    elif code == 4038:
        return 'application_fee não pode ser maior que transaction_amount.'
    elif code == 4039:
        return 'application_fee não pode ser um valor negativo.'
    elif code == 4050:
        return 'payer.email deve ser um e-mail válido.'
    elif code == 4051:
        return 'payer.email deve ter menos de 254 caracteres.'
    elif code == 7523:
        return 'Data de validade inválida.'
    elif code == 403:
        return 'pedido ruim'
    elif code == 4:
        return 'O chamador não está autorizado a acessar este recurso.'
    elif code == 3002:
        return 'O chamador não está autorizado a realizar esta ação.'
    elif code == 404:
        return 'pedido ruim'
    elif code == 2000:
        return 'Pagamento não encontrado'
    else:
        return 'Aconteceu algum erro inesperado. Verelifique os dados e tente novamente.'

""" Original messages:
1
Params Error.
3
Token must be for test.
5
Must provide your access_token to proceed.
23
The following parameters must be valid date and format (yyyy-MM-dd'T'HH:mm:ssz) date_of_expiration.
1000
Number of rows exceeded the limits.
1001
Date format must be yyyy-MM-dd'T'HH:mm:ss.SSSZ.
2001
Already posted the same request in the last minute.
2002
Customer not found.
2004
POST to Gateway Transactions API fail.
2006
Card Token not found.
2007
Connection to Card Token API fail.
2009
Card token issuer can't be null.
2060
The customer can't be equal to the collector.
3000
You must provide your cardholder_name with your card data.
3001
You must provide your cardissuer_id with your card data.
3003
Invalid card_token_id.
3004
Invalid parameter site_id.
3005
Not valid action, the resource is in a state that does not allow this operation. For more information see the state that has the resource.
3006
Invalid parameter cardtoken_id.
3007
The parameter client_id can not be null or empty.
3008
Not found Cardtoken.
3009
unauthorized client_id.
3010
Not found card on whitelist.
3011
Not found payment_method.
3012
Invalid parameter security_code_length.
3013
The parameter security_code is a required field can not be null or empty.
3014
Invalid parameter payment_method.
3015
Invalid parameter card_number_length.
3016
Invalid parameter card_number.
3017
The parameter card_number_id can not be null or empty.
3018
The parameter expiration_month can not be null or empty.
3019
The parameter expiration_year can not be null or empty.
3020
The parameter cardholder.name can not be null or empty.
3021
The parameter cardholder.document.number can not be null or empty.
3022
The parameter cardholder.document.type can not be null or empty.
3023
The parameter cardholder.document.subtype can not be null or empty.
3024
Not valid action - partial refund unsupported for this transaction.
3025
Invalid Auth Code.
3026
Invalid card_id for this payment_method_id.
3027
Invalid payment_type_id.
3028
Invalid payment_method_id.
3029
Invalid card expiration month.
3030
Invalid card expiration year.
4000
card atributte can't be null.
4001
payment_method_id atributte can't be null.
4002
transaction_amount atributte can't be null.
4003
transaction_amount atributte must be numeric.
4004
installments atributte can't be null.
4005
installments atributte must be numeric.
4006
payer atributte is malformed.
4007
site_id atributte can't be null.
4012
payer.id atributte can't be null.
4013
payer.type atributte can't be null.
4015
payment_method_reference_id atributte can't be null.
4016
payment_method_reference_id atributte must be numeric.
4017
status atributte can't be null.
4018
payment_id atributte can't be null.
4019
payment_id atributte must be numeric.
4020
notificaction_url atributte must be url valid.
4021
notificaction_url atributte must be shorter than 500 character.
4022
metadata atributte must be a valid JSON.
4023
transaction_amount atributte can't be null.
4024
transaction_amount atributte must be numeric.
4025
refund_id can't be null.
4026
Invalid coupon_amount.
4027
campaign_id atributte must be numeric.
4028
coupon_amount atributte must be numeric.
4029
Invalid payer type.
4037
Invalid transaction_amount.
4038
application_fee cannot be bigger than transaction_amount.
4039
application_fee cannot be a negative value.
4050
payer.email must be a valid email.
4051
payer.email must be shorter than 254 characters.
7523
Invalid expiration date.
403
bad_request
4
The caller is not authorized to access this resource.
3002
The caller is not authorized to perform this action.
404
bad_request
2000
Payment not found
"""
