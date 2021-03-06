from datetime import date
import src.connectRedis as connectRedis
import controllers.cassandra.cassandraSQL as cassandraCQL
import json

cursor = connectRedis.connect()
  
def create(request):
    body = request.get_json()

    title = body["title"]
    discount_percent = body["discount_percent"]
    in_operation = body["in_operation"]
    description = body["description"]
    expiration = body["expiration-in-seconds"]
    clause  = body["clause"]

    voucher_value = json.dumps(
      {
        "title": title,
        "discount_percent": discount_percent,
        "in_operation": in_operation,
        "description": description,
        "clause": clause
      }
    )

    try:
      if hasVoucher(title):
        return json.dumps({"status": "error", "message":"Cupom já cadastrado"})

      cursor.set(f'voucher:{title}', voucher_value)
      cursor.expire(f'voucher:{title}', expiration)
      cassandraCQL.create(voucher_value)

      return json.dumps({"status": "ok"})
    except: 
      return json.dumps({"status": "error"})

def index():
  return cassandraCQL.index()

def show(params):
  voucher_title = params.get("voucher-name")  

  return json.dumps(findVoucher(voucher_title))   

def update(request):
  voucher_title = request.args.get("voucher-name")
  body = request.get_json()

  if (hasVoucher(voucher_title)):    
    discount_percent = body["discount_percent"]
    in_operation = body["in_operation"]
    description = body["description"]
    expiration = body["expiration-in-seconds"]
    clause  = body["clause"]

    voucher_value = json.dumps(
      {
        "title": voucher_title,
        "discount_percent": discount_percent,
        "in_operation": in_operation,
        "description": description,
        "clause": clause
      }
    )
    try:
      cursor.set(f'voucher:{voucher_title}', voucher_value)
      cursor.expire(f'voucher:{voucher_title}', expiration)
      cassandraCQL.update(voucher_value)

      return json.dumps({"status": "ok"})
    except Exception as e: 
      return json.dumps({"status": e})
  else:
    return json.dumps({"status": "Not Found"})


def delete(params):
  voucher_title = params.get("voucher-name")  

  if (hasVoucher(voucher_title)):        
    try:
      cursor.delete(f'voucher:{voucher_title}')
      cassandraCQL.delete(voucher_title)

      return json.dumps({"status": "ok"})  
    except:
      return json.dumps({"hasError": True, "Message": "Não foi possível deletar cupom"})
  else:
    return json.dumps({"hasError": True, "Message": "Nenhum item encontrado"})

def findVoucher(voucherName):
  try:
    return json.loads(cursor.get(f'voucher:{voucherName}'))
  except:
    return json.dumps({"hasError": True, "Message": "Nenhum item encontrado"})

def hasVoucher(voucher_title):
  return cursor.exists(f'voucher:{voucher_title}') != 0
