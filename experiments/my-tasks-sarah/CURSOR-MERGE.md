# تجربة «مهامي» — سارة / خبزي الخالي

## ملفا التجربة (يفتحان في Cursor)

1. `experiments/my-tasks-sarah/CURSOR-MERGE.md` — هذا الدليل (لا يدخل في الرقعة)
2. `experiments/my-tasks-sarah/thabot-my-tasks.patch` — الرقعة الناجحة (تطبيق فقط)

معاينة عربية اختيارية بعد الدمج: `experiments/my-tasks-sarah/preview-my-tasks.html`

## أمر واحد جاهز للصق في Cursor (محاكي آيفون على Mac)

ضع الرقعة خارج المستودع (مثلاً `/tmp/thabot-my-tasks.patch`) حتى لا يتعارض الدليل مع `git apply`، ثم:

```bash
cd "$HOME/src/thabot-core" && git fetch origin dev && git checkout -B cursor/my-tasks-sarah-local origin/dev && git apply /tmp/thabot-my-tasks.patch && export PATH="$HOME/.local/bin:$PATH" && python3 -m pip install -q -r api/requirements-dev.txt && python3 -m pytest -q api/tests/test_my_tasks.py && python3 scripts/mint_local_mobile_session.py --who sarah --minutes 120 --write-env work/local-mobile.env >/tmp/thabot-local-session.json && (bash scripts/run_local_my_tasks_api.sh &) && sleep 3 && cd apps/mobile-board && export $(grep -E '^EXPO_PUBLIC_' ../../work/local-mobile.env | xargs) && export EXPO_PUBLIC_THABOT_LOCAL_TEST=1 EXPO_PUBLIC_THABOT_API_ORIGIN=http://127.0.0.1:8001 && pnpm install --frozen-lockfile && pnpm run ios
```

عدّل `cd "$HOME/src/thabot-core"` إلى مسار نسختك. التطبيق المشترك: `apps/mobile-board`.
الأمر أعلاه موجّه لـ **محاكي آيفون** على نفس Mac الذي يشغّل الخادم على `127.0.0.1`.

## السلوك

- الهوية والشركة من الجلسة الموثّقة فقط؛ لا يُقبل معرّف موظف من العميل.
- سارة: `emp_sarah_khubzi_001`، العرض «سارة»، المهمة «إعداد جدول إنتاج الأسبوع»، الموعد `2026-11-19`، المرجع `M-001 / D-01`.
- الاختبارات الأربعة + عزل عمر (خبزي الخالي) + عزل نوف (`gf` / مصنع سعودي جلوتين فري).

## تحقق بيئة Linux السحابية

- **على الخادم:** نجح — قائمة/تفاصيل سارة، عمر 404، اختبارات `test_my_tasks.py`، وعقد/مكوّنات الموبايل.
- **محاكي آيفون:** غير متاح هنا (Linux بلا Xcode). الأمر التالي على Mac: السطر أعلاه حتى `pnpm run ios`.

## أقصر خطوة بعد نجاح المحاكي — آيفون حقيقي بحساب شركة تجريبي

لا تستخدم `127.0.0.1` من الجهاز الحقيقي. بعد نجاح المحاكي محلياً: ارفع واجهة API على عنوان يصل إليه الجهاز (HTTPS على شبكة Mac أو نفق USB)، حدّث `EXPO_PUBLIC_THABOT_API_ORIGIN`، ثم `pnpm run ios -- --device` — بلا نشر ولا تغيير صلاحيات ولا ربط Odoo في هذه المرحلة.
