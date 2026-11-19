# มาตรฐานเงิน/ราคา (ทุก project)

> **กฎการคำนวณ + แสดงผล "เงิน" ในซอฟต์แวร์ ให้ตรงบัญชี/ภาษีไทย+สากล**
> บังคับใช้ทุกโปรเจกต์ (กฎอยู่ใน `rules/delivery.md` → "`reflex:money` / price discipline").
> **Gate skill:** บังคับใช้ผ่าน skill `reflex:money` — รันคู่กับ `reflex:verify-changes` ก่อน push (โครงเดียวกับ i18n-guard/design-system).
> หลักภาษีเหมือนกันทุก project → ห้ามปล่อยตามใจแต่ละที่. ของจริงเชิงโค้ดอยู่ใน repo (เช่น `src/lib/money.ts` + `docs/money-standard.md`).
> **ขอบเขต:** กฎนี้ = เงิน **fiat / บัญชี / ภาษี**. **ไม่ครอบ exchange/trading tick-size & precision** (เช่น trading bot snap ราคา/qty ตาม exchange filter = คนละ domain, ไม่มีเงินภาษี → ปล่อยให้ repo จัดการเอง ห้ามบังคับ Half-Up/2-ทศนิยมทับ).

## ทำไมต้องมี
ยอดเงินในบิล/บัญชีไม่ตรงกับระบบ = ปัญหาคลาสสิกจาก **ปัดเศษไม่เป็นมาตรฐาน** (ปัดคนละจุด, ลอย float, แสดงทศนิยมไม่คงที่). เรื่องนี้สำคัญ + ไม่ควรปล่อย เพราะกระทบใบกำกับภาษี/นำส่งสรรพากร.

## กฎหลัก
1. **เก็บ/คำนวณ ราคาต่อหน่วย · ต้นทุน · เรท · อัตราแลกเปลี่ยน:** ละเอียดได้ (4–6 ตำแหน่ง) — เก็บ raw, **อย่าปัดก่อนเวลา**
2. **แสดงผล + บันทึก ยอดเงิน / VAT / หัก ณ ที่จ่าย:** **2 ทศนิยมเสมอ** (`฿7,500.00` ไม่ใช่ `฿7,500`) — สอดคล้องหน่วย "สตางค์"
3. **ปัดเศษ Half-Up (5/4)** บนทศนิยมหลักที่ 3 → ใช้ `ROUND(x, 2)` ทุกจุดที่ตัดยอด (100.544→100.54 · 100.545→100.55) — ตาม ป.86/2542
4. **ลำดับคำนวณ (ปัดทีละสเต็ป กันส่วนต่าง):**
   ยอดรวม (ราคา×จำนวน, เก็บ full precision) → หักส่วนลด → **สุทธิ ปัด 2** → VAT 7% **ปัด 2** → รวมสุทธิ **2 ตำแหน่งถ้วน**
5. **cash rounding (เศษสตางค์หน้าเคาน์เตอร์)** = คนละเรื่อง: บิล/บัญชีเก็บ 2 ตำแหน่งตามจริง, ส่วนต่างจากการทอนเงินสดบันทึกเป็น "กำไร/ขาดทุนจากการปัดเศษ" (กรมการค้าภายใน) — ทำเมื่อมี POS เงินสดจริงเท่านั้น

## บังคับเชิงโค้ด (ทุก project)
- **ทุกการคำนวณ/แสดงเงิน ผ่าน money helper เดียวต่อแอป** (`lib/money.ts` หรือเทียบเท่า) — ห้าม `toLocaleString`/`toFixed`/แปะสัญลักษณ์เงินดิบ กระจายในโค้ด
- helper อย่างน้อยมี: `roundMoney(n)` (Half-Up กัน float — ใช้ snippet ใน § Reference snippet ด้านล่าง หรือ decimal lib; **ห้ามใช้ `Math.round((n + Number.EPSILON)*100)/100`** ผิดจริง), `fmtMoney(n, currency?)` (2 ตำแหน่งเสมอ + thousands), `parseMoney(str)`
- **multi-currency เบาๆ:** helper เป็นเจ้าของ **สัญลักษณ์ + จำนวนทศนิยม** ผ่าน config map (`THB → {symbol:'฿', decimals:2}`, ขยายภายหลังได้) — **ห้าม hardcode `฿` เป็น string กระจายทั่วโปรเจกต์** (default = THB); ไม่ต้องลง currency library เต็ม
- **input ราคา:** `type="number"` `min={0}` `step="0.01"` (ไม่ใช่ text + inputMode) + parse ผ่าน `parseMoney` — กันกรอกตัวอักษร/ค่าพัง
- **gate `check:money`** (เหมือน check:dates/check:pii): fail build ถ้ามี `toLocaleString` บนเงิน / สัญลักษณ์เงินดิบ / `toFixed` นอก helper (escape ด้วย tag เฉพาะกรณีตั้งใจ)

## Reference snippet (Half-Up, half away from zero)
> **snippet corrected — projects that copied an older snippet must be checked.**
> เดิมแนะนำ `Math.round((n + Number.EPSILON) * 100) / 100` → **ผิด 2 ทาง**: (1) float — `Number.EPSILON` (~2.2e-16) เล็กเกินกว่าจะชดเชย error ของ `n*100` ที่โตตามขนาดค่า → `2.135→2.13` (ต้อง 2.14); สแกนทุก x.xx5 ใน [0,1000) ผิด 4,573/100,000; (2) ค่าติดลบ — `Math.round` ปัด .5 เข้าหา +∞ → `-2.135→-2.13` (Excel `ROUND` = ปัดออกจากศูนย์ → -2.14); ลบ x.xx5 ผิด 95,425/100,000.

วิธีที่ถูก = **เลื่อนจุดทศนิยมใน string (exact) ไม่คูณเลข float** + ตัด noise ด้วย `toPrecision(15)` + ใส่เครื่องหมายทีหลัง:

```ts
export function roundMoney(n: number, decimals = 2): number {
  if (!Number.isFinite(n)) throw new RangeError('roundMoney: non-finite')
  const abs = Math.abs(n)
  if (abs < 1e-6) return 0 // sub-micro = 0 at any money precision (also dodges "1e-7e2" → NaN)
  if (abs >= 1e15) throw new RangeError('roundMoney: out of range')
  const clean = Number(abs.toPrecision(15)) // strip binary noise: 1.0049999999999999 → 1.005
  // shift the point in the STRING: "2.135e2" parses to exactly 213.5 (no float multiply)
  const r = Number(`${Math.round(Number(`${clean}e${decimals}`))}e-${decimals}`)
  return r === 0 ? 0 : n < 0 ? -r : r // sign applied after = half away from zero; no -0
}
```

ทางเลือก: เก็บเป็น **integer cents/สตางค์** ทั้งระบบ (ปัดครั้งเดียวตอนคูณ rate ด้วยฟังก์ชันด้านบน) หรือใช้ decimal lib — ห้ามกลับไป `(n + EPSILON) * 100`.

**Test vectors (ต้องผ่านทุก project):** `roundMoney(2.135) === 2.14` · `roundMoney(1.005) === 1.01` · `roundMoney(-2.135) === -2.14`
(snippet ข้างบนตรวจแล้ว: สแกนทุก x.xx5 ใน [0,1000) ทั้งบวก/ลบเทียบ Half-Up แบบ exact → ผิด 0; แนะนำให้ใส่ sweep test แบบนี้ใน `money.test.ts` ของทุก repo)

## อ้างอิง
สรรพากร ป.86/2542 (ใบกำกับภาษี) · ROUND(x,2) เป็นมาตรฐานสากล. แหล่ง: jsat66 (VAT & rounding), excelexperttraining (rounding with meaning), Oracle/ConstructionOnline (rounding rules). รายละเอียดเต็ม + ลิงก์ใน repo `docs/money-standard.md`.
