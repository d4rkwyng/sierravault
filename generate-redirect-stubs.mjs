// Fix ambiguous wikilinks. Entities that exist in more than one folder
// (e.g. Dynamix in both developers/ and publishers/) resolve to a bare `/slug`
// under Quartz's "shortest" link mode, which 404s. For every internal link that
// lands on a missing page, if a real page with that basename exists elsewhere,
// emit a small redirect stub at the broken location pointing to the canonical
// page (preferring developer > publisher > designer > series > …).
import fs from "fs"
import path from "path"

const ROOT = "public"
const PREF = ["developers", "publishers", "designers", "series", "games", "guides", "technology", "reference"]

function walk(dir) {
  let out = []
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name)
    if (e.isDirectory()) out = out.concat(walk(p))
    else if (e.name.endsWith(".html")) out.push(p)
  }
  return out
}

const files = walk(ROOT)
const byBase = new Map() // basename -> [site slug without .html]
for (const f of files) {
  const slug = f.slice(ROOT.length + 1, -5)
  const base = path.basename(slug)
  ;(byBase.get(base) ?? byBase.set(base, []).get(base)).push(slug)
}

const rank = (slug) => {
  const i = PREF.indexOf(slug.split("/")[0])
  return i === -1 ? 99 : i
}

const stubbed = new Set()
for (const f of files) {
  const dir = path.dirname(f)
  const html = fs.readFileSync(f, "utf8")
  for (const m of html.matchAll(/href="([^"]+)"/g)) {
    const href = m[1]
    if (/^(https?:|#|mailto:|\/static\/)/.test(href)) continue
    if (/\.(png|webp|jpg|jpeg|gif|svg|css|js|json|xml|ico|woff2?|pdf|zip)(\?|$)/i.test(href)) continue
    let clean
    try {
      clean = decodeURIComponent(href.split("#")[0].split("?")[0])
    } catch {
      continue // malformed percent-encoding in a href — not stub material
    }
    if (!clean || clean === "/") continue
    // absolute internal hrefs resolve from the site root, not the current page
    const target = path.normalize(clean.startsWith("/") ? path.join(ROOT, clean) : path.join(dir, clean))
    if (fs.existsSync(target + ".html") || fs.existsSync(path.join(target, "index.html")) || fs.existsSync(target)) continue
    const rel = path.relative(ROOT, target)
    if (rel.startsWith("..") || rel.includes(":")) continue
    const cands = byBase.get(path.basename(rel))
    if (!cands || !cands.length) continue
    const dest = "/" + [...cands].sort((a, b) => rank(a) - rank(b) || a.localeCompare(b))[0]
    const stubPath = path.join(ROOT, rel + ".html")
    if (stubbed.has(stubPath) || fs.existsSync(stubPath)) continue
    fs.mkdirSync(path.dirname(stubPath), { recursive: true })
    fs.writeFileSync(
      stubPath,
      `<!DOCTYPE html><html lang="en-us"><head><meta charset="utf-8"><link rel="canonical" href="${dest}"><meta http-equiv="refresh" content="0; url=${dest}"><title>Redirecting…</title></head><body>Redirecting to <a href="${dest}">${dest}</a>…</body></html>`,
    )
    stubbed.add(stubPath)
  }
}
console.log(`generated ${stubbed.size} redirect stubs for ambiguous wikilinks`)
