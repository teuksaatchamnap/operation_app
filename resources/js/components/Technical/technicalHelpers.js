export const urgencyColor = (u) => ({ critical: 'error', high: 'orange-darken-1', medium: 'warning', low: 'success' }[u] || 'default')

export const slaColor = (s) => s <= 4 ? 'text-green-darken-2' : s < 24 ? 'text-amber-darken-2' : 'text-red-darken-2'
