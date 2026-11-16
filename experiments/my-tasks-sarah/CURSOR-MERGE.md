# تجربة «مهامي» — سارة / خبزي الخالي

## ملفا التجربة (يفتحان في Cursor)

1. `experiments/my-tasks-sarah/CURSOR-MERGE.md` — هذا الملف
2. `experiments/my-tasks-sarah/thabot-my-tasks.patch` — الرقعة الناجحة

معاينة عربية للمحتوى: `experiments/my-tasks-sarah/preview-my-tasks.html`

## أمر واحد جاهز للصق في Cursor

يفترض أن المستودع `Aljazeerah-River/thabot-core` موجود محلياً، وأن ملف الرقعة بجانب هذا الملف:

```bash
cd "$HOME/src/thabot-core" && git fetch origin dev && git checkout -B cursor/my-tasks-sarah-local origin/dev && git apply experiments/my-tasks-sarah/thabot-my-tasks.patch && export PATH="$HOME/.local/bin:$PATH" && python3 -m pip install -q -r api/requirements-dev.txt && python3 -m pytest -q api/tests/test_my_tasks.py && python3 scripts/mint_local_mobile_session.py --who sarah --minutes 120 --write-env work/local-mobile.env >/tmp/thabot-local-session.json && (bash scripts/run_local_my_tasks_api.sh &) && sleep 3 && cd apps/mobile-board && export $(grep -v '^#' ../../work/local-mobile.env | xargs) && export EXPO_PUBLIC_THABOT_LOCAL_TEST=1 EXPO_PUBLIC_THABOT_API_ORIGIN=http://127.0.0.1:8001 && pnpm install --frozen-lockfile && pnpm run ios
```

عدّل `cd "$HOME/src/thabot-core"` إلى مسار نسختك. التطبيق المشترك المستهدف هو `apps/mobile-board`.

## السلوك

- الهوية والشركة من الجلسة الموثّقة فقط؛ لا يُقبل معرّف موظف من العميل.
- سارة: `emp_sarah_khubzi_001`، العرض «سارة»، المهمة «إعداد جدول إنتاج الأسبوع»، الموعد `2026-11-19`، المرجع `M-001 / D-01`.
- الاختبارات الأربعة + عزل عمر (خبزي الخالي) + عزل نوف (`gf` / مصنع سعودي جلوتين فري).

## تحقق بيئة Linux السحابية (هذا الوكيل)

- **على الخادم:** نجح — قائمة/تفاصيل سارة، عمر 404، اختبارات `test_my_tasks.py`، وعقد/مكوّنات الموبايل.
- **داخل محاكي آيفون:** لم يُشغَّل — العائق: المضيف Linux بلا Xcode/Simulator.
- **أمر التشغيل التالي على Mac:** الأمر أعلاه حتى `pnpm run ios`.

## أقصر خطوة متبقية على آيفون حقيقي بحساب شركة تجريبي

شغّل الأمر أعلاه على Mac مع الجهاز موصولاً (`pnpm run ios -- --device` إن لزم) وافتح «مهامي» بجلسة سارة المحلية — بلا نشر ولا تغيير صلاحيات ولا ربط Odoo في هذه المرحلة.
