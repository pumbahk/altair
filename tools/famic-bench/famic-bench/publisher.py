from kombu import Connection

with Connection('amqp://guest:guest@localhost:5672//') as conn:
    simple_queue = conn.SimpleQueue('receipt_queue')
    message = '575L2R12LH464'
    simple_queue.put(message)
    print('Sent: %s' % message)
    simple_queue.close()
