import json

def lambda_handler(event, context):
    for record in event['Records']:
        body = json.loads(record['body'])
        message = json.loads(body['Message'])

        message_attributes= body.get('MessageAttributes', {})
        event_type = message_attributes.get('eventType', {}).get('Value')

        event_id = message.get('eventId')
        order_id = message.get('orderId')
        customer = message.get('customer')
        amount = message.get('amount')

        items = message.get('items', {})
        item_id = items.get('itemId')
        quantity = items.get('quantity')

        if event_type == "ORDER_CREATED":
            if int(quantity) <= 0:
                raise ValueError("Incorrect quantity")
            
            if int(amount) < 0:
                raise ValueError("Incorrect amount")
            
            print(f"[ORDER_CREATED] eventId: {event_id} | orderId: {order_id}")
            print(f"{customer} ordered {quantity} of {item_id}")

        elif event_type == "ORDER_CANCELLED":
            print(f"[ORDER_CANCELLED] eventId: {event_id} | orderId: {order_id}")
            print(f"{customer} cancelled order {order_id}")

    return {
        'statusCode': 200,
        'body': 'Done'
    }