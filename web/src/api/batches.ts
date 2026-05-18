import { getJson, postFile, postJson } from './client'
import type {
  AiSummaryResponse,
  BatchDetail,
  BatchSummary,
  IntegrationName,
  IntegrationResponse,
} from './types'

export const uploadBatch = (file: File) =>
  postFile<BatchSummary>('/batches/upload', file)

export const getBatchDetail = (batchId: string) =>
  getJson<BatchDetail>(`/batches/${batchId}`)

export const generateAiSummary = (batchId: string) =>
  postJson<AiSummaryResponse>(`/batches/${batchId}/ai-summary`)

export const triggerIntegration = (batchId: string, name: IntegrationName) =>
  postJson<IntegrationResponse>(`/batches/${batchId}/integrations/${name}`)
