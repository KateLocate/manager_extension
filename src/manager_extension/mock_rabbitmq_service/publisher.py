import asyncio

import aio_pika


async def _main() -> None:
    IN, OUT = 'in', 'out'
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@rabbitmq/",
    )

    async with connection:
        channel = await connection.channel()

        # Will take no more than 10 messages in advance
        await channel.set_qos(prefetch_count=10)

        # Declare an exchange
        exchange = await channel.declare_exchange('base')
        # A queue
        in_queue = await channel.declare_queue(IN, auto_delete=True)
        # Bind the queue to the exchange
        await in_queue.bind(exchange)

        print('Enter RabbitMQ message input mode.\nIf you want to exit, use "Ctrl+C".')
        try:
            while True:
                msg = input('Message:')

                await exchange.publish(
                    aio_pika.Message(body=f"message: {msg}".encode()),
                    routing_key=IN,
                )
        except KeyboardInterrupt:
            print('Exit input mode.')


def main():
    asyncio.run(_main())


if __name__ == "__main__":
    main()
