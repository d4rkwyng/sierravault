#!/usr/bin/env node
// Prepend the release year to game titles ("1987 - Leisure Suit Larry ...").
// The explorer nav is built client-side from an index that doesn't carry
// release_year, so it can't sort/label by year on its own — baking the year
// into the title makes the nav show it and sort chronologically. Operates on
// the generated content/ copy only; the source vault/ is untouched.
import fs from "node:fs"
import path from "node:path"

const dir = process.argv[2] || "content"

function walk(d) {
  for (const e of fs.readdirSync(d, { withFileTypes: true })) {
    const p = path.join(d, e.name)
    if (e.isDirectory()) walk(p)
    else if (e.name.endsWith(".md")) {
      let s = fs.readFileSync(p, "utf8")
      s = s.replace(/^(---\r?\n)([\s\S]*?)(\r?\n---)/, (full, open, fm, close) => {
        const ry = fm.match(/^release_year:\s*(\d{4})/m)
        if (!ry) return full
        const y = ry[1]
        const fm2 = fm.replace(/^(title:\s*)(["']?)(.*)$/m, (f, pre, q, val) =>
          new RegExp("^" + y + "\\b").test(val) ? f : pre + q + y + " - " + val,
        )
        return open + fm2 + close
      })
      fs.writeFileSync(p, s)
    }
  }
}
walk(dir)
