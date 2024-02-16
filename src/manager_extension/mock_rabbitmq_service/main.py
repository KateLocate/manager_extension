import asyncio
import random

import aio_pika

IN, OUT = 'in', 'out'
EXCHANGE_NAME = 'base'


async def mock_process():
    delay = random.randint(1, 5)
    await asyncio.sleep(delay)


class RabbitMQManager:
    def __init__(self, rmq_url):
        self.rmq_url = rmq_url

        self.rmq_connection = None
        self.exchange = None
        self.in_queue = None
        self.out_queue = None

    async def get_connection(self):
        self.rmq_connection = await aio_pika.connect_robust(self.rmq_url)

    async def setup(self):
        # Channel
        channel = await self.rmq_connection.channel()
        # Will take no more than 10 messages in advance
        await channel.set_qos(prefetch_count=10)
        # Declare an exchange
        self.exchange = await channel.declare_exchange(EXCHANGE_NAME)
        # The queues
        self.in_queue = await channel.declare_queue(IN, auto_delete=True)
        self.out_queue = await channel.declare_queue(OUT, auto_delete=True)
        # Bind the queues to the exchange
        await self.in_queue.bind(self.exchange)
        await self.out_queue.bind(self.exchange)

    async def publish_msg(self, routing_key, msg):
        await self.exchange.publish(
            aio_pika.Message(body=msg.encode()),
            routing_key=routing_key,
        )

    async def process_queue_message(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        async with message.process():
            print(message.body)
            await mock_process()
            await self.publish_msg(OUT, message.body.decode('utf-8'))

    async def close_connection(self):
        await self.rmq_connection.close()


async def _main() -> None:
    rmq_manager = RabbitMQManager("amqp://guest:guest@rabbitmq/")
    await rmq_manager.get_connection()
    await rmq_manager.setup()

    messages_batch = ['a' * (i + 1) for i in range(1)]
    for message in messages_batch:
        await rmq_manager.publish_msg(IN, message)

    await rmq_manager.in_queue.consume(rmq_manager.process_queue_message)

    try:
        # Wait until terminate
        await asyncio.Future()
    finally:
        await rmq_manager.close_connection()


def main():
    asyncio.run(_main())


if __name__ == "__main__":
    main()
