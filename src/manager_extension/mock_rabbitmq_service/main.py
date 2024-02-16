import asyncio
import random

import aio_pika

IN, OUT = 'in', 'out'
EXCHANGE_NAME = 'base'


class BusinessProcessor:
    def __init__(self, rmq_manager):
        self.rmq_manager = rmq_manager
    
    @staticmethod
    async def mock_process():
        delay = random.randint(1, 5)
        await asyncio.sleep(delay)
    
    async def process_queue_message(self, message: aio_pika.abc.AbstractIncomingMessage) -> None:
        async with message.process():
            print(message.body)
            await self.mock_process()
            await self.rmq_manager.publish_msg(OUT, message.body.decode('utf-8'))
        

class RabbitMQManager:
    def __init__(self, rmq_url):
        self.rmq_url = rmq_url

        self.rmq_connection = None
        self.exchange = None
        self.in_queue = None
        self.out_queue = None

    async def connect(self):
        self.rmq_connection = await aio_pika.connect_robust(self.rmq_url)

    async def setup(self):
        await self.connect()
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

    async def consume_messages(self, func):
        await self.in_queue.consume(func)

    async def teardown(self):
        await self.rmq_connection.close()


async def _main() -> None:
    rmq_manager = RabbitMQManager("amqp://guest:guest@rabbitmq/")
    await rmq_manager.setup()
    
    business_processor = BusinessProcessor(rmq_manager)

    await rmq_manager.consume_messages(business_processor.process_queue_message)

    try:
        # Wait until terminate
        await asyncio.Future()
    finally:
        await rmq_manager.teardown()


def main():
    asyncio.run(_main())


if __name__ == "__main__":
    main()
