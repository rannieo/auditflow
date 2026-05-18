import { describe, expect, it } from 'vitest'
import { http, HttpResponse } from 'msw'
import { server } from '@/test/server'
import { getJson } from './client'

describe('api/client', () => {
  it('parses JSON on a 200', async () => {
    server.use(
      http.get('/api/test-json', () => HttpResponse.json({ hello: 'world' })),
    )

    const body = await getJson<{ hello: string }>('/test-json')

    expect(body).toEqual({ hello: 'world' })
  })

  it('throws an Error with the server detail on 4xx', async () => {
    server.use(
      http.get('/api/test-detail', () =>
        HttpResponse.json({ detail: 'Batch not found.' }, { status: 404 }),
      ),
    )

    await expect(getJson('/test-detail')).rejects.toThrow('Batch not found.')
  })

  it('falls back to statusText when the body has no detail', async () => {
    server.use(
      http.get('/api/test-no-detail', () =>
        HttpResponse.text('plain text body', { status: 500 }),
      ),
    )

    await expect(getJson('/test-no-detail')).rejects.toThrow(
      /Internal Server Error|Request failed/,
    )
  })
})
