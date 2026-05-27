/**
 * Async Leaflet loader — call getL() to get the Leaflet instance.
 * Uses dynamic import to avoid Vite minification collisions.
 */

let _L = null

export async function getL() {
  if (_L) return _L
  const mod = await import('leaflet')
  _L = mod.default || mod
  // Fix broken marker icons in Vite builds
  if (_L.Icon?.Default) {
    delete _L.Icon.Default.prototype._getIconUrl
    _L.Icon.Default.mergeOptions({
      iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
      iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
      shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
    })
  }
  return _L
}

export async function ensureLeafletCSS() {
  if (document.getElementById('leaflet-npm-css')) return
  const link = document.createElement('link')
  link.id = 'leaflet-npm-css'
  link.rel = 'stylesheet'
  link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'
  document.head.appendChild(link)
  await new Promise(r => { link.onload = r; link.onerror = r })
}
