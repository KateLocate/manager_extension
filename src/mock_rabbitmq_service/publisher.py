import asyncio

import aio_pika


async def main() -> None:
    connection = await aio_pika.connect_robust(
        "amqp://guest:guest@127.0.0.1/",
    )

    async with connection:
        print('Enter RabbitMQ input mode.\nIf you want to exit, use "Ctrl+C".')
        try:
            while True:
                routing_key = "test_queue"

                channel = await connection.channel()

                await channel.default_exchange.publish(
                    aio_pika.Message(body=f"Hello {routing_key}".encode()),
                    routing_key=routing_key,
                )
        except KeyboardInterrupt:
            print('Exit input mode.')


if __name__ == "__main__":
    asyncio.run(main())
