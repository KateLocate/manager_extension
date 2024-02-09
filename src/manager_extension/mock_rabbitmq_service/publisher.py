import asyncio
import random

import aio_pika

IN, OUT = 'in', 'out'
EXCHANGE_NAME = 'base'


async def _main() -> None:
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@rabbitmq/",
    )

    async with connection:
        exchange, in_queue, out_queue = await configure_rmq_structures(connection)

        messages_batch = ['a' * (i + 1) for i in range(10)]
        for message in messages_batch:
            await publish_msg(exchange, IN, message)

        async with in_queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    print(message.body)
                    if in_queue.name in message.body.decode():
                        break
                    await mock_process()
                    await publish_msg(exchange, OUT, message.body)


async def configure_rmq_structures(connection):
    # Configure RabbitMQ structures:
    # Channel
    channel = await connection.channel()
    # Will take no more than 10 messages in advance
    await channel.set_qos(prefetch_count=10)
    # Declare an exchange
    exchange = await channel.declare_exchange(EXCHANGE_NAME)
    # The queues
    in_queue = await channel.declare_queue(IN, auto_delete=True)
    out_queue = await channel.declare_queue(OUT, auto_delete=True)
    # Bind the queues to the exchange
    await in_queue.bind(exchange)
    await out_queue.bind(exchange)

    return exchange, in_queue, out_queue


async def publish_msg(exchange, routing_key, msg):
    await exchange.publish(
        aio_pika.Message(body=msg.encode()),
        routing_key=routing_key,
    )


async def mock_process():
    delay = random.randint(1, 5)
    await asyncio.sleep(delay)


def main():
    asyncio.run(_main())


if __name__ == "__main__":
    main()
