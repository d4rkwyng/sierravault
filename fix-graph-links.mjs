// The graph view (and backlinks) read public/static/contentIndex.json. Each
// node's `links` array holds the raw wikilink targets, which are bare and
// un-collapsed (e.g. "1995---torin's-passage") and so do NOT match the
// collapsed, full-path node slugs (e.g. "games/standalone/1995-torin's-passage").
// Result: the graph draws no edges. Remap every link target to the real node
// slug so edges connect.
import fs from "fs"

const PATH = "public/static/contentIndex.json"
const ci = JSON.parse(fs.readFileSync(PATH, "utf8"))
const keys = Object.keys(ci)

const byBase = new Map()
for (const k of keys) {
  const b = k.split("/").pop()
  ;(byBase.get(b) ?? byBase.set(b, []).get(b)).push(k)
}

let fixed = 0
for (const k of keys) {
  const node = ci[k]
  if (!Array.isArray(node.links)) continue
  node.links = node.links.map((l) => {
    if (ci[l]) return l // already a real node slug
    const collapsed = l.replace(/-{2,}/g, "-")
    if (ci[collapsed]) return collapsed // collapsed form is a real slug
    const cands = byBase.get(collapsed.split("/").pop())
    if (cands && cands.length) {
      fixed++
      return cands[0] // match by basename (folder was dropped in the link)
    }
    return collapsed
  })
}

fs.writeFileSync(PATH, JSON.stringify(ci))
console.log(`remapped ${fixed} graph link targets to real node slugs`)
