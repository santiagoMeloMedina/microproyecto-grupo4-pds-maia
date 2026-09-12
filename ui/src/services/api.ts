/**
 * Cliente de la API de riesgo de retraso.
 *
 * La URL base se toma de VITE_API_URL para que el mismo build sirva en local y
 * en el despliegue, donde la API vive en otro host. Ver ui/.env.example.
 */

const BASE_URL = (import.meta.env.VITE_API_URL ?? 'http://localhost:8002').replace(/\/$/, '')
const API_PREFIX = '/api/v1'

export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response

  try {
    response = await fetch(`${BASE_URL}${API_PREFIX}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...init,
    })
  } catch {
    // fetch solo rechaza por fallo de red o CORS, nunca por un codigo de error.
    throw new ApiError(
      `No se pudo contactar la API en ${BASE_URL}. Verifica que esté en ejecución.`,
      0,
    )
  }

  if (!response.ok) {
    const detail = await response.json().catch(() => null)
    throw new ApiError(detail?.detail ?? `La API respondió ${response.status}.`, response.status)
  }

  return (await response.json()) as T
}

/** Construye la query string omitiendo los filtros sin valor. */
function query(params: Record<string, string | number | undefined | null>): string {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== null && value !== '') {
      search.set(key, String(value))
    }
  }
  const texto = search.toString()
  return texto ? `?${texto}` : ''
}

export { request, query, BASE_URL }
