import json

def lambda_handler(event, context):
    for record in event['Records']:
        body = json.loads(record['body'])
        message = json.loads(body['Message'])

        message_attributes= body.get('MessageAttributes', {})
        event_type = message_attributes.get('eventType', {}).get('Value')
        payment_method = message_attributes.get('paymentMethod', {}).get('Value')

        event_id = message.get('eventId')
        order_id = message.get('orderId')
        customer = message.get('customer')
        amount = message.get('amount')
        
        items = message.get('items', {})
        quantity = items.get('quantity')

        if event_type == "ORDER_CREATED" and payment_method in ["CARD", "MOMO"]:
            if int(quantity) <= 0:
                raise ValueError("Incorrect quantity")
            
            if int(amount) < 0:
                raise ValueError("Incorrect amount")
        
            print(f"[PAYMENT_ORDER_CREATED] eventId: {event_id} | orderId: {order_id}")
            print(f"{customer} pay with {payment_method}")

    return {
        'statusCode': 200,
        'body': 'Done'
    }