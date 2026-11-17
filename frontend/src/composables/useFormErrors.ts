import { reactive } from 'vue'

export interface FormErrorMap {
  [field: string]: string[]
}

export function useFormErrors<T extends Record<string, unknown>>(fieldNames: (keyof T)[]) {
  const errors = reactive<Record<string, string>>({})

  // Initialize empty error strings for each known field
  fieldNames.forEach((field) => {
    errors[field as string] = ''
  })

  function clearErrors(): void {
    fieldNames.forEach((field) => {
      errors[field as string] = ''
    })
  }

  /**
   * Map backend validation details (field -> messages) onto local errors.
   * Only the first message is shown per field to keep UI clean.
   */
  function mapApiErrors(details?: FormErrorMap | null): void {
    clearErrors()
    if (!details) return
    Object.entries(details).forEach(([field, messages]) => {
      if (errors[field] !== undefined && Array.isArray(messages) && messages.length > 0) {
        errors[field] = messages[0]
      }
    })
  }

  /**
   * Set a manual error for a specific field.
   */
  function setError(field: string, message: string): void {
    if (errors[field] !== undefined) {
      errors[field] = message
    }
  }

  return {
    errors,
    clearErrors,
    mapApiErrors,
    setError,
  }
}
