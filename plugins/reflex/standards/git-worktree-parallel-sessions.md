# Git Worktree — Parallel Sessions

> Reference ถาวร — ทำไม/เมื่อไร/อย่างไร ของ `git worktree` สำหรับงานขนานหลาย session
> กฎ + auto-detect อยู่ใน `rules/delivery.md` § Ship discipline · official docs: <https://git-scm.com/docs/git-worktree>

## Why — the one-tree problem

- Working tree 1 ชุด = **branch 1 อัน + index (staging) 1 อัน** — นี่คือข้อจำกัดเชิงโครงสร้างของ git ไม่ใช่เรื่อง discipline
- 2 sessions แชร์ tree เดียว → session B สลับ branch = ไฟล์ถูกดึงออกใต้เท้า session A · WIP ชนกัน · commit ทับไฟล์ของอีก session · branch-guard จับผิด branch
- `git worktree add` = checkout **เพิ่มอีกชุด** จาก repo เดิม (แชร์ `.git` object store — เบากว่า clone ใหม่มาก) → แต่ละ session ได้ tree + branch + index ของตัวเอง แยกขาดกัน

## Machine rule — auto-detect, every session

ทุก session ตรวจเองก่อน **แก้ไฟล์/สร้าง branch/commit ครั้งแรก** ใน repo — เจอ signal ใดข้อหนึ่ง → เปิด worktree ทันทีโดยไม่ต้องถาม:

1. `git status` มี changes ที่ session นี้ **ไม่ได้ทำ** (WIP ของ session อื่น)
2. checkout อยู่บน branch ที่ session นี้ไม่ได้สร้าง (ไม่ใช่ default branch)
3. user บอกว่ามีงานคู่ขนาน / รู้อยู่แล้วว่ามี session อื่น active ใน repo นี้
4. `git worktree list` แสดง worktree อื่น active อยู่

ไม่มี signal + tree สะอาด → ทำงานใน checkout หลักตามปกติ (ไม่ต้องเปิด worktree เปล่าๆ ให้เปลือง setup)

## Mechanics — Claude Code path

- `EnterWorktree` → สร้างที่ `.claude/worktrees/<name>` แตกจาก `origin/<default>` · **1 branch = 1 worktree**
- Worktree ใหม่ = สะอาดเรื่อง deps/secrets: ต้อง `bun install` + copy `.env` (gitignored) ก่อน build gates จะผ่าน
- Rename branch อัตโนมัติ `worktree-*` → `feat/...` ก่อนเปิด PR
- จบงาน: merge แล้ว `ExitWorktree` (worktree ที่ไม่มี change ถูกเก็บกวาดอัตโนมัติ)

## Mechanics — raw git

```bash
git worktree add ../feat-x -b feat/x     # tree ใหม่ + branch ใหม่
git worktree add ../hotfix origin/main   # detached จาก main
git worktree list                        # ดูทุก tree ที่ active
git worktree remove <path>               # ปิด tree ที่จบงาน
git worktree prune                       # เก็บกวาด metadata ค้าง
```

## Caveats

- **Branch เดียว checkout ได้ใน worktree เดียว** — git กันเองโดย design (กัน index ชนกัน)
- Object store + refs + stash **แชร์กัน** ทุก worktree (fetch ครั้งเดียวเห็นหมด) · HEAD/index/untracked files **แยกกัน** ต่อ worktree
- Path ของ worktree ต้องถูก gitignore (`.claude/worktrees/` ถูก ignore อยู่แล้วใน scaffold)
- Submodule support ยังไม่สมบูรณ์ (repo ในเครื่องนี้ไม่ใช้ submodule — ไม่กระทบ)
