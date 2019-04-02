import socket
import asyncio
import time
import logging
import random

from apps.HelloWorld.v1_0.src.app import HelloWorld

async def stream_of_consciousness(sentences):
	intervals = [1, 2, 5, 10]
	coros = []
	for sentence in sentences:
		app = HelloWorld()
		when = random.choice(intervals)
		coros.append(app.hello(sentence, when))
	for next_sentence in asyncio.as_completed(coros):
		return await next_sentence

if __name__ == '__main__':
    sentences = ['a', 'b', 'c']

    loop = asyncio.get_event_loop()
    loop.run_until_complete(stream_of_consciousness(sentences))