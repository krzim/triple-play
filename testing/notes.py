@pytest.mark.asyncio
async def test_create_connection(conn):
    await conn.execute('set', 'hello', 'create_redis')
    val = await conn.execute('get', 'hello')
    assert val == b'create_redis'


@pytest.mark.asyncio
async def test_create_pool(pool):
    await pool.execute('set', 'hello', 'create_pool')
    val = await pool.execute('get', 'hello')
    assert val == b'create_pool'


@pytest.mark.asyncio
async def test_pubsub(redis_pool):
    res = await redis_pool.subscribe('chan')
    channel = res[0]
    await redis_pool.publish('chan', 'hello')
    msg = await channel.get()
    assert msg == b'hello'


@pytest.mark.asyncio
async def test_auth(server):
    r1 = await birdisle.aioredis.create_redis(server)
    await r1.config_set('requirepass', 'p@ssword')
    await r1.auth('p@ssword')
    await r1.set('foo', 'bar')
    r1.close()
    await r1.wait_closed()

    with pytest.raises(aioredis.AuthError):
        r2 = await birdisle.aioredis.create_redis(server)
        await r2.get('foo')

    r3 = await birdisle.aioredis.create_redis(server, password='p@ssword')
    assert await r3.get('foo') == b'bar'