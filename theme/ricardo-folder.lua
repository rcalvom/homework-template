-- =====================================================================
--  theme/ricardo-folder.lua
--  Read a folder of .tex fragments and \input them in name order.
--
--  Loaded by theme/ricardo-homework.sty, which wraps this in \DocFolder.
--
--  Lua and not TeX because TeX cannot list a directory. LuaTeX can, through
--  lfs, which is built into the engine -- no shell escape, no external
--  process, no generated file to keep in step with the folder.
-- =====================================================================

local M = {}

-- Every .tex in <dir>, sorted by name.
--
-- table.sort is a plain byte comparison, which is what the ordering promise
-- needs: it does not depend on a locale, so the document comes out in the
-- same order on every machine. It is also why the shipped files are numbered
-- in tens -- 010, 020 -- rather than counted. `10' sorts before `9', and a
-- set that renumbers itself whenever a problem is inserted is worse than one
-- that leaves gaps.
local function fragments(dir)
  local found = {}
  if lfs.attributes(dir, "mode") ~= "directory" then
    return nil
  end
  for name in lfs.dir(dir) do
    -- Dotfiles are an editor's business, not the document's. `_'-prefixed
    -- files are shared includes, pulled in by name where they are wanted.
    if name:sub(1, 1) ~= "." and name:sub(1, 1) ~= "_"
       and name:sub(-4) == ".tex" then
      found[#found + 1] = name
    end
  end
  table.sort(found)
  return found
end

-- \DocFolder{<dir>}
function M.folder(dir)
  local found = fragments(dir)
  if not found then
    tex.error("Fragment folder not found: " .. dir,
              { "\\DocFolder was given a path that is not a directory.",
                "Paths are relative to the folder you run the engine from,",
                "which for this template is always the repository root." })
    return
  end
  if #found == 0 then
    texio.write_nl("Package ricardo Warning: no fragments in " .. dir)
    return
  end
  -- One \input per file, built as a single string. TeX reads what it is
  -- given front to back, and each \input runs to completion before the next
  -- begins, so the order is not in question.
  local out = {}
  for _, name in ipairs(found) do
    out[#out + 1] = "\\input{" .. dir .. "/" .. name .. "}"
  end
  tex.sprint(table.concat(out))
end

return M
