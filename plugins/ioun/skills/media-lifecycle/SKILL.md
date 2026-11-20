---
name: media-lifecycle
description: Whenever a change touches user-uploaded media (images, photos, files) — capture, upload, display, replace, or delete — apply the three media rules: (1) STAGE, don't eager-upload — hold the file client-side, upload only on final submit; (2) NO ORPHANS — removing a file or deleting a record that owns files must delete the storage object too; (3) VIEW = LIGHTBOX — every displayed image is tappable to fullscreen with zoom + swipe. Stack-agnostic; auto-detects the storage layer. Run alongside verify-changes and i18n-guard before pushing.
---

# media-lifecycle

A convention + commit-time gate for **user-uploaded media** (images/photos/files in
object storage — S3, Cloudflare R2, Supabase Storage, GCS, …). Eager uploads and
missing deletes silently bloat a bucket forever; dead thumbnails frustrate users.
When a change captures, uploads, shows, replaces, or deletes media, make it obey the
three rules below. Stack-agnostic — detect the project's setup first, then act.

## 0. Detect the setup (before touching anything)

- **Where do bytes live?** Find the upload helper (grep `PutObject`, `upload`, `s3`,
  `r2`, `getSignedUrl`, `createReadStream`, `storage.from(...).upload`). Note the
  bucket + how a stored **URL maps back to an object key** (you'll need the key to
  delete). If the public URL is `host + '/' + key`, the key is `new URL(url).pathname`
  minus the leading slash.
- **Who owns the lifecycle?** If a CMS/framework manages it (e.g. **Payload**, Strapi,
  Supabase with storage RLS + triggers), it usually deletes objects on record delete —
  **don't double-handle**; verify it actually does and move on. The rules below target
  **hand-rolled** storage code, which almost never cleans up by default.
- **What records own media?** List the tables/collections with a URL/key column or a
  join table of photos. Every one is a deletion site (Rule 2).

## 1. STAGE, don't eager-upload

The picked/captured file is held in **client state** (a `File`/`Blob`), previewed
locally (`URL.createObjectURL`), and uploaded to storage **only when the user commits**
(create / save / confirm). Never upload on file-pick or on camera-capture.

**Why:** a user who picks a photo, changes their mind, picks another, then cancels must
leave **zero** bytes in the bucket. Eager upload-on-pick strands every discarded attempt.

- Pickers return files to the parent; the parent uploads inside the submit handler.
- Multi-step/array pickers stage an **array** of files + a list of removed-existing ids;
  the submit applies both (upload new, delete removed) in one go.
- Single-action flows (a status change that needs a photo) stage the file and upload it
  **inside that one action**, not before it.
- Acceptable exception: an explicit standalone "Upload now" affordance on an already-saved
  record (no draft to discard). Even then, Rule 2 still applies on later removal.

## 2. NO ORPHANS — delete bytes when the reference dies

Every path that drops a media reference must drop the **object** too:

- **Remove a staged (not-yet-uploaded) file** → just drop it from state. Nothing in storage.
- **Remove a saved image** → delete the storage object AND its DB row/field.
- **Delete a record that owns images** (item, post, product, the parent order, a gallery)
  → collect its object keys, delete the objects, then let the rows cascade.
- **Replace an image** = remove old + add new; the old object must be deleted, not left.

Implementation notes:
- Provide a small **delete-by-url / delete-by-id** helper next to the upload helper
  (`keyFromUrl` + `DeleteObject`). Make it **best-effort** (`allSettled`) so an
  already-gone object never blocks the DB write.
- Collect keys **before** the rows cascade away (you can't read them after).
- Do the object delete **after** the DB change commits (don't delete bytes for a write
  that then rolls back). For a hard record-delete: read keys → delete rows → delete objects.
- Soft-delete/archive does NOT delete objects (the record may come back) — only hard
  deletes and explicit removals do.

## 3. VIEW = LIGHTBOX

Any image rendered to the user is **tappable** → opens a fullscreen viewer with
**zoom** (pinch / wheel) and, when it belongs to a set, **swipe/keyboard paging** across
the whole array. No dead thumbnails the user can't enlarge.

- Prefer a small, touch-solid library over a hand-rolled pinch-zoom (the math is fiddly
  on mobile) — unless the project deliberately avoids deps, then build it but cover
  pinch + double-tap + swipe.
- One shared viewer component, reused at every display site (forms, detail pages, galleries).
- Open at the tapped index; pass the item's full image array so paging works.

## 4. Report (end of a media-touching change)

State briefly:
- **Staged?** every new picker holds files client-side, uploads on submit (or names the
  justified exception).
- **Orphans?** every removal + every owning-record delete now deletes objects; list the
  deletion sites you wired.
- **Lightbox?** every newly-shown image is tappable → fullscreen + zoom + swipe.
- **Left immediate-upload or dead thumbnails anywhere?** Call it out explicitly with why.

## Anti-patterns (reject these)

- `onChange={() => upload()}` / upload-on-capture in a form — strands discarded picks.
- Deleting a row/record that has images without deleting the objects — silent bloat.
- Storing only a URL with no way back to the key — you can't delete; keep the key
  derivable (host+key) or store the key.
- `<img>` thumbnails with no click target — users can't read detail in the photo.
- A bespoke pinch-zoom that breaks on real phones — use a proven viewer.
