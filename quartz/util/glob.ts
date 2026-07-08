import path from "path"
import { FilePath } from "./path"
import { globby } from "globby"

export function toPosixPath(fp: string): string {
  return fp.split(path.sep).join("/")
}

export async function glob(
  pattern: string,
  cwd: string,
  ignorePatterns: string[],
): Promise<FilePath[]> {
  const fps = (
    await globby(pattern, {
      cwd,
      ignore: ignorePatterns,
      // We generate content/ at build time and keep it gitignored (it lives in
      // the separate sierravault content repo). Don't let .gitignore hide it
      // from the content glob — ignorePatterns still covers .obsidian etc.
      gitignore: false,
    })
  ).map(toPosixPath)
  return fps as FilePath[]
}
