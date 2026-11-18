# تسليم حالة سحابة ثابوت — مرجع تنفيذي للوكيل المنفّذ

| البند | القيمة |
|---|---|
| التاريخ | 2026-10-27 (الأوقات بتوقيت UTC ما لم يُذكر غير ذلك) |
| المصدر | جلسة Claude (Cowork) عبر Cloud Shell بحساب `asem.alkahtani@aljazeerahriver.com` |
| مستوى الثقة | كل ما في الأقسام 1–9 **فحص حي مباشر** في هذا التاريخ، ما لم يُكتب «غير مثبت» |
| الجمهور | المؤسس، والوكيل المنفّذ (Codex)، والمراجعون التقنيون والقانونيون |
| قاعدة | لا توجد في هذه الوثيقة أي قيمة سرية أو توكن. أسماء الأسرار فقط |

---

## 0. الخلاصة في عشرة أسطر

1. الجسر `odoo-thabot-bridge` بإصدار **2.1.1-hardened** يعمل على prod وdev، مغلق أمام العموم (403 بدون توكن)، وبلا أي ربطات IAM عامة.
2. **لا يوجد أي مستخدم حقيقي** للجسر، ولا يوجد اتصال حقيقي بـOdoo: الرابط المضبوط يحوّل إلى صفحة مشروع Odoo.sh (القاعدة متوقفة أو محذوفة).
3. أدوات الكتابة في الجسر **مرفوضة حالياً عمداً** (fail-closed)، لأن `sa-thabot` لا يملك صلاحية Firestore بعد.
4. سير النشر القديم من GitHub **غير قادر على النشر اليوم** (لا هوية صالحة ولا صلاحية نشر)، لكنه لم يُعطَّل في GitHub.
5. مصدر الجسر المحصّن موجود في حزمة `thabot-bridge-2.1.1-hardened.zip` وفي Cloud Shell، **وليس في أي مستودع Git بعد** (البند B00).
6. `thabot-core-api` (أُنشئ 19 أكتوبر) يعمل بنموذج `gemini-2.5-flash` مع `allow_global_fallback`، **ولا يوجد أي استخدام فعلي له**: كل طلباته تقريباً من مراقب Google.
7. Cloud SQL (`thabot-pg-instance-prod`) يكلّف نحو 35 دولاراً شهرياً، **ولا يستهلكه أي خدمة تشغيلية**، لكنه مُعدّ بستة أدوار مستأجرين.
8. الإنفاق: **64.38 دولاراً من 1 إلى 26 أكتوبر**، والتوقع **113.14 دولاراً** لشهر أكتوبر.
9. سياسة تقييد النطاقات **غير مطبقة** (الكل مسموح)، وتوجد دعوة ملكية معلّقة لحساب Gmail شخصي.
10. المرحلة 0 (قرارات المؤسس) هي العائق الحقيقي، لا التقنية.

---

## 1. هوية المشروع والمؤسسة

| البند | القيمة |
|---|---|
| معرّف المشروع | `thabot` |
| رقم المشروع | `221375339753` |
| المنطقة | `me-central2` (الدمام) |
| السلسلة الهرمية | المشروع `thabot` ← المجلد `811914382678` ← المؤسسة `939093040049` |
| اسم المؤسسة | `aljazeerahriver.com` |
| معرّف عميل Workspace | `C00nqraek` |
| حساب الفوترة | `019FD8-DE9E4F-5C42BD` |
| تحذير | الرقم `214562874507` ظهر في رابط صفحة الفوترة فقط، **وليس مؤسسة هذا المشروع**. لا يُستخدم في أوامر السياسات |
| رابط Cloud Run المشترك للمشروع | `*-rpgkxttijq-wx.a.run.app` و `*-221375339753.me-central2.run.app` |

### مالكو المشروع والهويات

| الهوية | الدور |
|---|---|
| `user:asem.alkahtani@aljazeerahriver.com` | owner |
| `user:dr.asem@thabot.com` | owner |
| `user:hamad@thabot.com` | owner |
| `user:AASEM303@gmail.com` | `roles/resourcemanager.projectOwnerInvitee` (**دعوة ملكية معلّقة لم تُقبل**) |
| `serviceAccount:221375339753@cloudservices.gserviceaccount.com` | editor (حساب Google داخلي افتراضي) |

---

## 2. خدمات Cloud Run (5 خدمات)

| الخدمة | المراجعة الحية | الحالة | حساب التشغيل | ملاحظات |
|---|---|---|---|---|
| `prod-odoo-thabot-bridge` | `prod-odoo-thabot-bridge-00008-gos` (100%، وسم `hardened`) | 2.1.1-hardened | `sa-thabot` | IAM مفعّل، 403 بدون توكن، بلا ربطات |
| `dev-odoo-thabot-bridge` | `dev-odoo-thabot-bridge-00015-bad` (100%، وسم `hardened`) | 2.1.1-hardened | `sa-thabot` | IAM مفعّل، 403 بدون توكن، بلا ربطات |
| `odoo-thabot-bridge` | لا توجد | **معطّلة** منذ 2026-09-07 (`RevisionFailed`، الصورة محذوفة) | الحساب الافتراضي compute | بلا رابط، **0 طلب في 30 يوماً**. مرشحة للحذف |
| `thabot-configure1` | `thabot-configure1-00003-wx2` | صورة فارغة `gcr.io/cloudrun/placeholder` | الحساب الافتراضي compute | IAM مفعّل (403). مرشحة للحذف |
| `thabot-core-api` | `thabot-core-api-00011-vtn` | تعمل | `thabot-app-sa` | انظر القسم 6 |

### مراجعات التراجع (ما قبل التحصين — فيها الثغرات القديمة)
- prod: `prod-odoo-thabot-bridge-00004-c44`
- dev: `dev-odoo-thabot-bridge-00005-ps2`

### مراجعات تشخيصية يجب حذفها (أنشأتها جلسة التحصين)
- `dev-odoo-thabot-bridge-00008-toy` و `dev-odoo-thabot-bridge-00010-zuh`: تشغّلان خادماً بسيطاً يعيد ترويسات الطلب (مقطوعة إلى 30 حرفاً). **بلا حركة مرور وبلا وسم**، فلا يمكن الوصول إليهما، لكن يجب حذفهما حتى لا يُعاد وسم إحداهما بالخطأ.
- مراجعات وسيطة بلا حركة: dev `00007-din` و`00011-veg` و`00012-faw`، وprod `00006-waj`.

---

## 3. الجسر: الشفرة القديمة (ما كان يعمل قبل 27 أكتوبر)

استُخرجت الشفرة من صورتي prod وdev مباشرة (لم يكن لها مستودع معروف). الصورتان متطابقتان سطراً بسطر.

| البند | القيمة |
|---|---|
| تاريخ بناء الصور | 2026-09-07 |
| المستودع في Artifact Registry | `me-central2-docker.pkg.dev/thabot/odoo-thabot-bridge-repo/{prod,dev}-odoo-thabot-bridge` |
| الصورة القديمة لـ`odoo-thabot-bridge` | `me-central2-docker.pkg.dev/thabot/thabot-repo/odoo-thabot-bridge` (**محذوفة**) |
| الملفات | `main.py` (206 سطر)، `config.py` (39)، `api/governance.py` (26)، `governance/kill_switch.py` (98)، `Dockerfile`، `pyproject.toml`، `uv.lock`، `gha-creds-*.json` |
| الإطار | FastAPI + `mcp==1.8.0` (FastMCP) على المسار `/mcp/`، عميله المقصود Gemini |

### الثغرات المؤكدة في الشفرة القديمة
1. **[حرج]** مفتاح خاص لحساب `sa-thabot` مضمّن في الصورة (`gha-creds-*.json`)، لأن `Dockerfile` ينسخ `COPY . /app` دون `.dockerignore`. المفتاح (`7566bed11cd4…`، أُنشئ 2026-09-06) **معطّل الآن، لكنه لم يُحذف**.
2. **[حرج]** أداة MCP الوحيدة `query_odoo` تنفّذ `search_read` مفتوحاً: العميل يحدد النموذج والحقول والفلتر والحد، ولا يوجد تقييد بالشركة.
3. **[حرج]** وسيط HTTP يسجّل جميع الترويسات الخام (ومنها `Authorization`).
4. **[عالٍ]** `/api/v1/governance/kill` بلا مصادقة، و`/reset` يقارن برمز ثابت مكتوب في الشفرة (يُعامل كمكشوف). حالة الإيقاف في `/tmp` لكل نسخة على حدة.
5. **[متوسط]** إرجاع `str(e)` للعميل، وخلل `RecursionError` في `CloudLoggingFormatter` عند وجود استثناء.

---

## 4. الجسر: الإصدار المحصّن 2.1.1-hardened (الحي الآن)

### الصورة والإعداد
| البند | القيمة |
|---|---|
| الصورة (index digest) | `me-central2-docker.pkg.dev/thabot/odoo-thabot-bridge-repo/dev-odoo-thabot-bridge@sha256:b4f109269fa249e8c8e90207828977f7aa5429ca4eb63034a5e5930031f2259a` |
| الوسم في Artifact Registry | `hardened-2-1-3` (وسوم قديمة: `hardened-2-1-0` و`-2-1-1` و`-2-1-2`) |
| الأساس | `python:3.12-slim`، مستخدم غير جذري `appuser`، بلا أي ملف json |
| متغيرات Odoo | `ODOO_URL` و`ODOO_DB` و`ODOO_USER` نصية، و`ODOO_PASSWORD` من السر `thabot-odoo-api-key:1` (إصدار مثبت) |
| متغير إلزامي جديد | `ALLOWED_AUDIENCES=["32555940559.apps.googleusercontent.com","618104708054-9r9s1c4alg36erliucho9t52n32n6dgq.apps.googleusercontent.com"]` |
| صيغة gcloud للمتغير | `--update-env-vars='^@^ALLOWED_AUDIENCES=[...]'` (الفاصل `@` لأن القيمة فيها فواصل) |

### الإصدارات المثبتة (requirements.txt)
`mcp==1.8.0`، `fastapi==0.141.1`، `starlette==1.6.0`، `anyio==4.15.1`، `uvicorn[standard]==0.52.4`، `gunicorn==26.2.0`، `pydantic==2.13.5`، `pydantic-settings==2.15.0`، `python-dotenv==1.2.3`، `tenacity==9.1.4`، `google-auth==2.62.0`، `requests==2.34.2`، `google-cloud-firestore==2.34.1`

### الواجهات
| المسار | الوصف |
|---|---|
| `GET /health` | يعيد قيمة ثابتة: `{"status":"online","system":"odoo-bridge","version":"2.1.1-hardened"}` ولا يقرأ الطلب (اختُبر على الروابط الأربعة) |
| `POST /mcp/` (و`/mcp` يُعاد كتابته) | FastMCP، أداتان |
| أداة `query_odoo(model, domain, fields, limit)` | قراءة فقط، قائمة بيضاء لـ11 نموذجاً وحقولها، `1 ≤ limit ≤ 100`، فلتر الشركة يُفرض من الخادم: `'|', company_id=False, company_id in [ids]` |
| أداة `propose_waste_draft(...)` | تكتب مسودة في Firestore فقط (`thabot_waste_drafts`)، لا تلمس Odoo. منع تكرار ذري. **fail-closed** |
| `GET /api/v1/governance/status` و`POST /kill` و`POST /reset` | لمسؤولي الحوكمة فقط (هوية موثقة + قائمة `GOVERNANCE_ADMINS`) |
| `/docs` و`/redoc` و`/openapi.json` | معطّلة |

النماذج المسموحة في `query_odoo`: `product.product`، `product.template`، `stock.quant`، `stock.picking`، `stock.scrap`، `mrp.production`، `mrp.bom`، `sale.order`، `purchase.order`، `res.partner`، `fleet.vehicle`.

### حقائق منصة اكتُشفت بالاختبار (مهمة لأي شفرة مستقبلية على Cloud Run)
1. **بدون `lifespan` يتعطل FastMCP المركّب كلياً**: كل طلب يفشل بـ`Task group is not initialized`. المسودة التي اقترحها وكيل آخر كانت ستكسر `/mcp` بالكامل.
2. **Cloud Run يغيّر الترويسة إلى `bearer` بحروف صغيرة**، ويستبدل توقيع التوكن بالنص `SIGNATURE_REMOVED_BY_GOOGLE` بعد أن يتحقق منه بنفسه. التحقق التشفيري داخل التطبيق يفشل لذلك.
3. **الحل المطبّق**: قبول التوكن مجرّد التوقيع فقط عند `TRUST_CLOUD_RUN_IAM=true`، مع فحص `iss` و`exp` و`email_verified` و`aud`. أي توكن آخر يُتحقق منه تشفيرياً.
4. **شرط أمني ملزم**: هذا القبول آمن فقط ما دام فحص Invoker IAM مفعّلاً ولا يوجد `allUsers`. فحص `aud` **لا يمنع التزوير** إن فُتح الوصول العام (المزوّر يكتب `aud` الصحيح)، بل يمنع إعادة استخدام توكن حقيقي لخدمة أخرى.
5. `aud` لتوكن `gcloud` على جهاز = `32555940559.apps.googleusercontent.com`، وفي Cloud Shell = `618104708054-9r9s1c4alg36erliucho9t52n32n6dgq.apps.googleusercontent.com`. التوكن بين الخدمات يحمل رابط الخدمة.
6. **`gcloud run deploy` يرث `--command/--args` من المراجعة السابقة**. يجب تمريرهما فارغين صراحة إذا كانت المراجعة السابقة تشخيصية.
7. Docker في Cloud Shell يدفع OCI index؛ Cloud Run يعرض بصمة صورة linux/amd64 (`2d4e18…` لا تساوي بصمة الـindex). هذا طبيعي.

### الاختبارات
- **محلياً**: 32 فحصاً نجحت كلها (Python 3.13، نفس الإصدارات المثبتة، مع محاكاة Odoo وFirestore): القائمة البيضاء، الحد، الحقول، العزل، منع التكرار، تعارض الحمولة، `/kill` و`/reset` بلا توكن، الإيقاف، fail-closed، 413، `/docs`، التوكن مجرّد التوقيع بحالاته (صالح، منتهٍ، جهة مُصدرة خاطئة، بريد غير موثق، توقيع مزور، `aud` خاطئ، `aud` غائب، `aud` الخدمة نفسها، `aud` خدمة شقيقة، الثقة معطّلة).
- **على السحابة**: 403 بدون توكن، `/health`، قائمة الأدوات، رفض `res.users` و`limit=0`، تعرّف الحوكمة على المسؤول، رفض الكتابة عند تعذر Firestore، خلو السجلات من التوكنات.
- **ملاحظة للمنفّذ**: ملفا الاختبار يفترضان مجلداً اسمه `app/` بجوارهما (`sys.path.insert(0, "app")`). عدّل المسار عند وضعها في `services/odoo-bridge/`.

### بصمات الحزمة (أول 12 حرفاً من SHA-256) — مطابقة لـCloud Shell
| الملف | البصمة |
|---|---|
| `.dockerignore` | `54fb6cf5f674` |
| `Dockerfile` | `4bd23b243655` |
| `requirements.txt` | `c9a0bfec43b6` |
| `config.py` | `f4eea5d8cc36` |
| `main.py` | `4ec8b08c7401` |
| `api/governance.py` | `954c51a5c475` |
| `governance/kill_switch.py` | `92aac6c71514` |

الحزمة `thabot-bridge-2.1.1-hardened.zip` تحتوي أيضاً `DEPLOYMENT.md` و`tests/test_app.py` و`tests/test_auth.py`.

---

## 5. الأسرار وحسابات الخدمة

### الأسرار (Secret Manager)
| السر | من يقرؤه | ملاحظات |
|---|---|---|
| `thabot-odoo-api-key` | `sa-thabot` | الإصدار 1 فقط (أُنشئ 2026-09-06)، مثبت في الخدمتين. **يجب تدويره** بعد إصلاح Odoo |
| `odoo-bridge-api-key` | `thabot-app-sa` | — |
| `thabot-odoo-password` | `thabot-gateway-runner` | **غير مستخدم** من أي خدمة |
| `odoo-api-token` | لا أحد على مستوى السر | — |
| `thabot-postgres-master-password` | لا أحد على مستوى السر | يخص Cloud SQL |

### حسابات الخدمة
| الحساب | الأدوار | المفاتيح |
|---|---|---|
| `sa-thabot@thabot.iam.gserviceaccount.com` | `roles/aiplatform.user`، `roles/logging.logWriter`، قراءة `thabot-odoo-api-key` | مفتاح واحد `7566bed11cd4…` **معطّل** (لم يُحذف) |
| `thabot-app-sa@thabot.iam.gserviceaccount.com` | يشغّل `thabot-core-api`، مستخدم IAM في Cloud SQL، يقرأ `odoo-bridge-api-key` | لا يوجد |
| `thabot-gateway-runner@thabot.iam.gserviceaccount.com` | أُنشئ اليوم، قراءة `thabot-odoo-password` فقط | لا يوجد. **مرشح للحذف** (غير مستخدم) |
| `221375339753-compute@developer.gserviceaccount.com` | `artifactregistry.writer`، `developerconnect.readTokenAccessor`، `logging.logWriter`، `storage.objectViewer` | لا يوجد |
| Workload Identity Pools | **لا يوجد أي pool** | — |

---

## 6. `thabot-core-api` ومزود الذكاء الاصطناعي

| البند | القيمة |
|---|---|
| أُنشئ | 2026-10-19 بين 04:03 و04:20 UTC، بحساب `asem.alkahtani@aljazeerahriver.com` (Audit Logs) |
| الصورة | `me-central2-docker.pkg.dev/thabot/thabot-docker-repo/thabot-core@sha256:3a27192d45b47528bff2680ee3ea8d3aead4cfce6cafdd25256c572db36f7881` |
| مستودع الشفرة | **غير مثبت** |
| الإعدادات | `MODEL_NAME=gemini-2.5-flash`، `ROUTING_MODE=allow_global_fallback`، `APP_VERSION=0.3.4`، و`PROJECT_ID` و`THINKING_BUDGET` |
| الشبكة | لا VPC، ولا اتصال Cloud SQL |
| الوصول | IAM مفعّل (403 بدون توكن) |
| الاستخدام في 7 أيام | 12,035 طلباً بحالة 200، و2 بحالة 403، و1 بحالة 404 |
| مصدر الطلبات | كلها تقريباً من **Uptime Check** باسم «THABOT Core Health Check» كل 300 ثانية من عدة مناطق على `/health` (نحو 1,700 طلب يومياً) |
| الطلبات غير الآلية | 7 فقط في 7 أيام (`GET` على `/health` و`/` و`/openapi.json`)، **ولا يوجد أي POST**، أي لا استخدام فعلي للنموذج |

**أثر على قرار المزود**: `allow_global_fallback` يسمح بمعالجة الطلبات عبر نقطة Gemini عالمية خارج السعودية إذا تعذر النموذج في المنطقة. وثائق Codex تذكر أن `me-central2` لا يوفّر نماذج Gemini توليدية، بل نماذج التضمين فقط. إذا كان بقاء البيانات في السعودية شرطاً ملزماً، فهذا الإعداد يخالفه، ولا يوجد اليوم استخدام فعلي يتأثر بتغييره.

---

## 7. البيانات والتخزين

### Cloud SQL
| البند | القيمة |
|---|---|
| المثيل | `thabot-pg-instance-prod` |
| المحرك | PostgreSQL 16 |
| المنطقة / الفئة | `me-central2` / `db-custom-2-7680` |
| أُنشئ | 2026-10-19 |
| العنوان | خاص فقط `10.53.0.3`، بلا IP عام، بلا شبكات مصرّح بها |
| النسخ الاحتياطي | مفعّل؛ آخر نسخ ناجحة: 24 و25 و26 أكتوبر. **تجربة الاستعادة لم تُجرَ** |
| قواعد البيانات | `postgres`، `thabot_db` |
| المستخدمون | `postgres`، `thabot_app`، `thabot-app-sa@thabot.iam`، و6 أدوار مستأجرين: `role_tenant_nahr_aljazeera`، `role_tenant_khobzi_alkhali`، `role_tenant_gf_factory`، `role_tenant_thabot_tech`، `role_tenant_sbu_01`، `role_tenant_sbu_02` |
| من يصل إليه | **لا أحد تشغيلياً**: لا خدمة Cloud Run مربوطة، ولا VPC connector، ولا VMs، ولا Cloud Functions. توجد مهمتا تهيئة فقط: `init-db-job` و`thabot-db-setup-job` |
| تسجيلات الدخول في 7 أيام | 0 في السجلات (غير قاطع، فتسجيل الاتصالات قد يكون معطّلاً) |
| التكلفة | 35.04 دولاراً في أكتوبر حتى 26 منه (بند جديد) |

### Firestore
- قاعدة `(default)`، `FIRESTORE_NATIVE`، `me-central2`.
- يستخدمها الجسر: `thabot_governance/kill_switch` و`thabot_waste_drafts`.
- **`sa-thabot` لا يملك `roles/datastore.user`**؛ النتيجة: `/status` يعرض `{"killed":false,"readable":false}` وأدوات الكتابة مرفوضة.

### Odoo
| البند | القيمة |
|---|---|
| `ODOO_URL` المضبوط | `https://thabot-alkahtani-thabot-odoo-sytem2.odoo.com` |
| الاستجابة | `302` إلى `https://www.odoo.sh/project/thabot-alkahtani-thabot-odoo-sytem2` على `/xmlrpc/2/common` (http وhttps) |
| المعنى | القاعدة متوقفة أو محذوفة أو نُقلت. **لا يوجد اتصال Odoo حقيقي** |
| غير مثبت | القاعدة الصحيحة، إصدار Odoo، هل الخطة تسمح بالـAPI الخارجي، معرّف شركة نهر الجزيرة (`res.company`) |

---

## 8. GitHub والنشر

| البند | القيمة |
|---|---|
| آخر نشر من حساب خدمة | 2026-09-07، كله من `sa-thabot` (8 على dev و4 على prod). لا شيء بعده |
| لماذا لا يستطيع السير القديم النشر الآن | حاجزان: (أ) لا هوية صالحة — المفتاح الوحيد معطّل ولا WIF؛ (ب) لا صلاحية نشر — `sa-thabot` بلا أدوار Cloud Run |
| من يستطيع النشر اليوم | المالكون الثلاثة فقط |
| متى يعود الخطر | إذا أُعيد تفعيل المفتاح أو أُنشئ مفتاح جديد **مع** منح صلاحية نشر |
| مشغلات Cloud Build | `cloudrun-thabot-configure1-me-central2-AljazeerahRiver-thabovnd` و`cloudrun-thabot-agents-cli-git-me-central2-AljazeerahRiver-tmsc` (مربوطة بمنظمة GitHub `AljazeerahRiver` عبر Developer Connect) |
| بناءات سابقة | بناءات باسم `odoo-thabot-bridge` في 2026-08-07 و2026-08-15 من أرشيفات مصدر، وبناء فاشل `aljazeerahriver-thabot_syn-to-github` في 2026-08-07 |
| `gs://thabot-staging-bucket` | **غير موجود** (404) رغم ذكره في تقارير سابقة |
| غير مثبت | خطة GitHub، والـrulesets، والمتعاونون، ومحتوى سير العمل في `bridge666` و`sytem666` |

---

## 9. الحوكمة والسياسات

| البند | القيمة |
|---|---|
| سياسة `iam.allowedPolicyMemberDomains` الفعّالة على المشروع | `allValues: ALLOW` (**لا تقييد**) |
| حسابات من خارج النطاقين في IAM | `AASEM303@gmail.com` فقط (دعوة ملكية معلّقة) |
| غير مثبت | هل `thabot.com` نطاق ثانوي داخل نفس Workspace (`C00nqraek`) أم حساب مستقل. يُعرف من Admin Console: Account ← Domains |

---

## 10. الإنفاق (حساب الفوترة `019FD8-DE9E4F-5C42BD`)

| البند | المبلغ (USD) |
|---|---|
| الإجمالي 1–26 أكتوبر | **64.38** (زيادة 260% عن 5–30 سبتمبر) |
| التوقع لشهر أكتوبر كاملاً | **113.14** |
| Cloud SQL | 35.04 (جديد) |
| Duet AI (اشتراك Gemini Code Assist) | 15.53 |
| Cloud Run | 12.56 (استخدام 17.78 ناقص توفير 5.22) |
| فحص ثغرات Container Registry | 1.04 (جديد) |
| Cloud DNS | 0.16 |
| Vertex AI | 0.05 |

ملاحظة: التقرير على مستوى حساب الفوترة (يغطي 8 مشاريع)، لكن ملخص Google نسب Cloud SQL وCloud Run إلى مشروع Thabot.

---

## 11. Cloud Shell (بيئة العمل التي حدث فيها التحصين)

| البند | القيمة |
|---|---|
| القرص | ممتلئ **98%** (4.4 من 4.8 جيجابايت) |
| أكبر استهلاك | `~/.cache` بحجم 1.4 جيجابايت (`~/.cache/pip` آمن للمسح) |
| `~/bridge_src/hardened` | مصدر 2.1.1 (مطابق للحزمة) |
| `~/bridge_src/prod` و`~/bridge_src/dev` | الشفرة القديمة المستخرجة، **وتحتوي نسخاً من ملف المفتاح المعطّل** `gha-creds-*.json`. تُحذف |

---

## 12. أوامر للمالك (لم ينفذها أي وكيل — كلها بقرارك)

```bash
# أ) صلاحية Firestore (تفعّل مفتاح الإيقاف وأدوات الكتابة)
gcloud projects add-iam-policy-binding thabot \
  --member="serviceAccount:sa-thabot@thabot.iam.gserviceaccount.com" \
  --role="roles/datastore.user" --condition=None

# ب) حذف نسخ المفتاح من Cloud Shell، ثم المفتاح نفسه من IAM
rm -f ~/bridge_src/*/gha-creds-*.json
gcloud iam service-accounts keys list --iam-account=sa-thabot@thabot.iam.gserviceaccount.com --managed-by=user
gcloud iam service-accounts keys delete <KEY_ID_الكامل> --iam-account=sa-thabot@thabot.iam.gserviceaccount.com

# ج) حذف الخدمات والمراجعات الميتة (التحقق يدعم ذلك)
gcloud run services delete odoo-thabot-bridge --region=me-central2 --project=thabot
gcloud run services delete thabot-configure1 --region=me-central2 --project=thabot
gcloud run revisions delete dev-odoo-thabot-bridge-00008-toy --region=me-central2 --project=thabot
gcloud run revisions delete dev-odoo-thabot-bridge-00010-zuh --region=me-central2 --project=thabot
gcloud iam service-accounts delete thabot-gateway-runner@thabot.iam.gserviceaccount.com --project=thabot

# د) سحب دعوة الملكية المعلّقة (إن لم تكن مقصودة)
gcloud projects remove-iam-policy-binding thabot \
  --member="user:AASEM303@gmail.com" --role="roles/resourcemanager.projectOwnerInvitee"

# هـ) تقييد النطاقات على المشروع وحده (بعد التأكد من وضع thabot.com؛ أضف معرّفه إن كان Workspace مستقلاً)
gcloud resource-manager org-policies allow iam.allowedPolicyMemberDomains C00nqraek --project=thabot

# و) تحديث رابط Odoo بعد معرفته (على الخدمتين)
gcloud run services update prod-odoo-thabot-bridge --region=me-central2 --project=thabot \
  --update-env-vars=ODOO_URL=<الرابط_الصحيح>,ODOO_DB=<اسم_القاعدة>

# ز) التراجع الطارئ إلى ما قبل التحصين (يعيد الثغرات القديمة — للطوارئ فقط)
gcloud run services update-traffic prod-odoo-thabot-bridge --region=me-central2 --project=thabot \
  --to-revisions=prod-odoo-thabot-bridge-00004-c44=100
```

---

## 13. قرارات المرحلة 0 مع ما يعرفه الوكلاء عنها

| # | القرار | ما ثبت | ما يلزم منك |
|---|---|---|---|
| 1 | Odoo | الرابط الحالي ميت (302 إلى Odoo.sh) | القاعدة الصحيحة، رابطها، اسمها، إصدارها، هل الخطة تسمح بالـAPI، معرّف شركة نهر الجزيرة |
| 2 | Cloud SQL | مُعدّ بستة أدوار مستأجرين، نسخ يومية ناجحة، لا مستهلك تشغيلي، 35 دولاراً شهرياً | تخصيصه لثابوت (مع تجربة استعادة) أو نسخه ثم إيقافه |
| 3 | الذكاء الاصطناعي | `gemini-2.5-flash` مع `allow_global_fallback`؛ لا نماذج توليدية في `me-central2`؛ لا استخدام فعلي | هل بقاء البيانات في السعودية ملزم؟ إن نعم: الشريحة الأولى بلا مساعد، وتغيير `ROUTING_MODE` |
| 4 | الخط الواحد | 4 خطوط توحيد متوازية؛ نسخة العمل المحلية فيها 75 تعديلاً غير ملتزم | أي خط يبقى |
| 5 | المسؤول الواحد | من يملك النشر اليوم: المالكون الثلاثة | شخص بشري يملك الدمج والنشر |
| 6 | الشركات الست | أسماء تقنية في قاعدة البيانات: nahr_aljazeera، khobzi_alkhali، gf_factory، thabot_tech، sbu_01، sbu_02 | الأسماء القانونية والمالك لكل شركة (يكفي الآن نهر الجزيرة) |

---

## 14. تعليمات للوكيل المنفّذ

**افعل:**
1. أدخل الحزمة `thabot-bridge-2.1.1-hardened.zip` إلى `services/odoo-bridge/` في فرع منفصل: طابق البصمات السبع، وشغّل الاختبارات الـ32 وسجّل النتيجة الفعلية، وراجع الفرق بحثاً عن أسرار.
2. احمل `ALLOWED_AUDIENCES` في أي إعداد نشر مستقبلي، وإلا رفضت الحوكمة توكنات المسؤولين.
3. عند بناء سير CI للجسر: استخدم Workload Identity Federation، وانشر بالبصمة (`@sha256:`) مع `--no-traffic` ثم الاختبار ثم التحويل، ومرّر `--command=''` و`--args=''`.
4. سجّل في الوثائق أن قبول التوكن مجرّد التوقيع مشروط ببقاء IAM مفعّلاً، واربطه بالبوابة G1.

**لا تفعل:**
1. لا تنشر من Cloud Shell، ولا تستخدم `--allow-unauthenticated` على أي خدمة.
2. لا تعِد تفعيل مفتاح `sa-thabot` ولا تنشئ مفتاحاً جديداً.
3. لا تفعّل أي أداة كتابة على Odoo قبل مطابقة أرقام `res.company` الفعلية مع `ACTOR_ALLOWED_COMPANIES` (الافتراضي الحالي 1–6 تخميني).
4. لا تنقل أي جزء من توكن أو قيمة سر إلى الوثائق.
5. لا تعتبر أعداد طلبات `thabot-core-api` استخداماً فعلياً؛ مصدرها المراقب.

---

## 15. ما لم يُثبت بعد (قائمة مفتوحة)

- قاعدة Odoo الصحيحة وخطتها ومعرّف الشركة.
- مستودع شفرة `thabot-core-api`.
- خطة GitHub، والـrulesets، والمتعاونون، ومحتوى سير العمل في `bridge666` و`sytem666`.
- تجربة استعادة Cloud SQL.
- وضع نطاق `thabot.com` في Workspace.
- الأسماء القانونية للشركات الست ومالكوها.
- هل تسجيل الاتصالات مفعّل في Cloud SQL (لتأكيد عدم الاستخدام).
