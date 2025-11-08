/**
 * TypeScript declarations for Knot SDK (KnotapiJS)
 * https://docs.knotapi.com/sdk/web
 */

type Environment = 'development' | 'production'
type Product = 'card_switcher' | 'transaction_link'

interface KnotOpenConfig {
  sessionId: string
  clientId: string
  environment: Environment
  product: Product
  merchantIds?: number[]
  entryPoint?: string
  useCategories?: boolean
  useSearch?: boolean
  cardName?: string
  customerName?: string
  logoId?: number
  onSuccess?: (product: Product, details: { merchantName: string }) => void
  onError?: (product: Product, errorCode: string, errorDescription: string) => void
  onEvent?: (
    product: Product,
    event: string,
    merchant: string,
    merchantId: number,
    payload: any,
    taskId: string
  ) => void
  onExit?: (product: Product) => void
}

declare class KnotapiJS {
  constructor()
  open(config: KnotOpenConfig): void
}

interface Window {
  KnotapiJS?: {
    default: typeof KnotapiJS
  }
}

