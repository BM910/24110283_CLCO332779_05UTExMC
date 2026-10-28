import json

def lambda_handler(event, context):
    for record in event['Records']:
        body = json.loads(record['body'])
        message = json.loads(body['Message'])

        message_attributes = body.get('MessageAttributes', {})
        event_type = message_attributes.get('eventType', {}).get('Value')

        event_id = message.get('eventId')
        order_id = message.get('orderId')
        customer = message.get('customer')
        amount = message.get('amount')
        
        items = message.get('items', {})
        quantity = items.get('quantity')

        if event_type == "ORDER_CREATED":
            if int(quantity) <= 0:
                raise ValueError("Incorrect quantity")
            
            if int(amount) < 0:
                raise ValueError("Incorrect amount")
            
            print(f"[EMAIL_ORDER_CREATED] eventId: {event_id} | orderId: {order_id}")
            print(f"Send confirmation email to [{customer}]: Order {order_id} worth {amount} has been created")

        elif event_type == "ORDER_CANCELLED":
            print(f"[EMAIL_ORDER_CANCELLED] eventId: {event_id} | orderId: {order_id}")
            print(f"Send cancellation email to [{customer}]: Order {order_id} has been cancelled")

        elif event_type == "ORDER_SHIPPED":
            print(f"[EMAIL_ORDER_SHIPPED] eventId: {event_id} | orderId: {order_id}")
            print(f"Send email to [{customer}]: Order {order_id} is in shipping")

    return {
        'statusCode': 200,
        'body': 'Email Consumer Done'
    }