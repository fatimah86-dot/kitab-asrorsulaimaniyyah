#!/usr/bin/env python3
"""Blok NORMALISASI_NAHWU_FALAK_2026_10_05.

Dua pekerjaan (keduanya pada kolom Latin / catatan editorial berkas BATCH_*.md dan turunannya):

1. Catatan editorial berbahasa Inggris  ->  catatan Arab.
   Kaidah baku: «القراءة محتملة، والحروف محفوظة وفق الطباعة» (qiraatuhu muhtamalah,
   al-huruf mahfuzhah wifqa al-thiba'ah). Seluruh 228 catatan unik diterjemahkan
   satu per satu di PETA; tidak ada terjemahan mesin/tanpa peta.

2. Emendasi nahwu & falak halaman cetak 4 (PDF 5): «أي ما درى» (muharraf)
   ->  «وَأَيْنَمَا دَارَ» = dimanapun beredar (yakni di manapun benda langit itu
   beredar pada burujnya). Bentuk cetak tetap dicatat pada catatan (tidak diubah
   diam-diam), sesuai kaidah edisi repo.

Pakai:
    python tools/normalisasi_nahwu_falak.py            # terapkan ke berkas
    python tools/normalisasi_nahwu_falak.py --cek      # hanya periksa (harus 0 Inggris)
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# 1. Peta catatan editorial: Inggris -> Arab
#    (sisi kiri bebas tanda kutip/titik; dibandingkan setelah kanon()).
# ---------------------------------------------------------------------------

PETA: list[tuple[str, str]] = [
    # --- pola yang sering berulang (10x, 7x, 6x, ...) ---
    ("phonetic reading is tentative; printed consonants are retained",
     "القراءة محتملة، والحروف محفوظة على رسم المطبوع - qiraatuhu muhtamalah"),
    ("phonetic reading of the non-Arabic name is tentative; printed consonants are retained",
     "القراءة محتملة، والحروف محفوظة على رسم المطبوع - qiraatuhu muhtamalah"),
    ("the non-Arabic name is tentative; printed consonants retained",
     "القراءة محتملة، والحروف محفوظة على رسم المطبوع - qiraatuhu muhtamalah"),
    ("the name “Liyashishu” is tentative; printed consonants are retained",
     "اسم «ليشيشو» محتمل، والحروف محفوظة على رسم المطبوع"),
    ("ending unclear", "آخر الكلمة غير واضح"),
    ("ending unreadable", "آخر الكلمة غير مقروء"),
    ("ending obscured", "آخر الكلمة مطموس"),
    ("short ending unclear", "آخر قصير غير واضح"),
    ("short ending obscured", "آخر قصير مطموس"),
    ("short word unclear", "كلمة قصيرة غير واضحة"),
    ("short word after wa-law unclear", "كلمة قصيرة بعد «ولو» غير واضحة"),
    ("following word unclear", "الكلمة التالية غير واضحة"),
    ("following word unreadable", "الكلمة التالية غير مقروءة"),
    ("following word obscured", "الكلمة التالية مطموسة"),
    ("short middle word unclear", "كلمة وسطى قصيرة غير واضحة"),
    ("short middle word uncertain", "كلمة وسطى قصيرة غير محققة"),
    ("short fragment unclear", "شظية قصيرة غير واضحة"),
    ("short fragments unclear", "شظايا قصيرة غير واضحة"),
    ("short continuation unclear", "تتمة قصيرة غير واضحة"),
    ("short continuation faint", "تتمة قصيرة باهتة"),
    ("short phrase unclear", "عبارة قصيرة غير واضحة"),
    ("short phrase after ma unclear", "عبارة قصيرة بعد «ما» غير واضحة"),
    ("short separator or word between the epithets unclear",
     "فاصل أو كلمة قصيرة بين النعوت غير واضح"),
    ("short printed connector unclear", "رابط مطبوع قصير غير واضح"),
    ("short printed fragment unclear", "شظية مطبوعة قصيرة غير واضحة"),
    ("short printed fragment obscured", "شظية مطبوعة قصيرة مطموسة"),
    ("short name unclear", "اسم قصير غير واضح"),
    ("short name-like token obscured", "مقطع قصير شبيه باسم مطموس"),
    ("vocative name unreadable", "اسم النداء غير مقروء"),
    ("vocative name unclear", "اسم النداء غير واضح"),
    ("vocative name faint", "اسم النداء باهت"),
    ("vocative word unclear", "كلمة النداء غير واضحة"),
    ("opening word unreadable", "أول الكلمة غير مقروء"),
    ("opening word unclear", "أول الكلمة غير واضح"),
    ("remainder obscured", "البقية مطموسة"),
    ("remainder unreadable", "البقية غير مقروءة"),
    ("remainder faint", "البقية باهتة"),
    ("following name unclear", "الاسم التالي غير واضح"),
    ("following fragment unclear", "الشظية التالية غير واضحة"),
    ("following fragments unreadable", "الشظايا التالية غير مقروءة"),
    ("following name fragments unreadable", "شظايا الاسم التالية غير مقروءة"),
    ("following name-like fragment unclear", "الشظية التالية الشبيهة باسم غير واضحة"),
    ("following name/word unreadable", "الاسم/الكلمة التالية غير مقروءة"),
    ("following short tokens are indistinct through the line ending",
     "المقاطع القصيرة التالية غير متمايزة حتى آخر السطر"),
    ("fragment unclear", "الشظية غير واضحة"),
    ("fragment after the verb unclear", "الشظية بعد الفعل غير واضحة"),
    ("connected fragment unclear", "شظية متصلة غير واضحة"),
    ("connected, unclear ending", "آخر متصل غير واضح"),
    ("unclear connected ending", "آخر متصل غير واضح"),
    ("continuation obscured", "التتمة مطموسة"),
    ("continuation unreadable", "التتمة غير مقروءة"),
    ("faint continuation", "تتمة باهتة"),
    ("faint ending", "آخر باهت"),
    ("faint line ending", "آخر سطر باهت"),
    ("line edge faint", "حرف السطر باهت"),
    ("line edge unclear", "حرف السطر غير واضح"),
    ("line continuation unreadable", "تتمة السطر غير مقروءة"),
    ("line ending obscured", "آخر السطر مطموس"),
    ("line ending unreadable", "آخر السطر غير مقروء"),
    ("line ending uncertain", "آخر السطر غير محقق"),
    ("line-ending mark unreadable", "علامة آخر السطر غير مقروءة"),
    ("the line continuation is obscured", "تتمة السطر مطموسة"),
    ("the line ending is unclear", "آخر السطر غير واضح"),
    ("ending unclear.", "آخر الكلمة غير واضح"),
    ("the ending is tentative", "الآخر محتمل"),
    ("tentative ending", "آخر محتمل"),
    ("final form tentative", "الصيغة الأخيرة محتملة"),
    ("tentative reading", "قراءة محتملة"),
    ("tentative reading of the final word", "قراءة محتملة للكلمة الأخيرة"),
    ("the last form is uncertain", "الصيغة الأخيرة غير محققة"),
    ("vowels unknown", "الحركات مجهولة"),
    ("proper name, approximate", "اسم علم، تقريبي"),
    ("talismanic name", "اسم طلسمي"),
    ("name-like word resembling “ghiyaha”", "كلمة شبيهة باسم، تشبه «غياهه»"),
    ("name resembling “shankh/shunukh”", "اسم يشبه «شنخ/شنوخ»"),
    ("following name has letters resembling “tantanj”", "الاسم التالي حروفه تشبه «تنتنج»"),
    ("short token resembling “kand”", "مقطع قصير يشبه «كند»"),
    ("token resembling “mawla”", "مقطع يشبه «مولى»"),
    ("word begins “hayatina”", "الكلمة تبدأ بـ«حياتنا»"),
    ("unclear name", "اسم غير واضح"),
    ("unclear name-like fragment", "شظية شبيهة باسم غير واضحة"),
    ("unclear name-like sequence", "تسلسل شبيه باسم غير واضح"),
    ("unclear name/fragment", "اسم/شظية غير واضحة"),
    ("unclear name/word", "اسم/كلمة غير واضحة"),
    ("unclear fragment", "شظية غير واضحة"),
    ("unclear word", "كلمة غير واضحة"),
    ("unclear talismanic words", "كلمات طلسمية غير واضحة"),
    ("unreadable talismanic name", "اسم طلسمي غير مقروء"),
    ("name-like fragment unclear", "شظية شبيهة باسم غير واضحة"),
    ("name-like word unclear", "كلمة شبيهة باسم غير واضحة"),
    ("name/word resembles “tambas”", "الاسم/الكلمة يشبه «طمبس»"),
    ("printed fragment unreadable", "شظية مطبوعة غير مقروءة"),
    ("final word unreadable", "الكلمة الأخيرة غير مقروءة"),
    ("the line ending resembles “zahamat”", "آخر السطر يشبه «زحمت»"),
    ("line ending appears to read “tasallatat”", "يظهر آخر السطر مقروءًا «تسلطت»"),
    ("verb form retained as printed", "صيغة الفعل محفوظة وفق المطبوع"),
    ("talismanic words retained as printed", "كلمات طلسمية محفوظة وفق المطبوع"),
    ("talismanic name begins “tahtabiyal”", "اسم طلسمي يبدأ بـ«تهتبيال»"),

    # --- "resembles / tentatively" ---
    ("ending resembles “'athurat”", "الآخر يشبه «عثرت»"),
    ("ending resembles “bishamilat”", "الآخر يشبه «بشملت»"),
    ("ending resembles “jallalat”", "الآخر يشبه «جللت»"),
    ("ending resembles “na'bat”", "الآخر يشبه «نعبت»"),
    ("ending resembles “sukhkhirat”", "الآخر يشبه «سخرت»"),
    ("ending resembles “tabat”", "الآخر يشبه «تبت»"),
    ("ending resembles “tasajamat”", "الآخر يشبه «تسجمت»"),
    ("the ending resembles asbalt", "الآخر يشبه «أسبلت»"),
    ("the ending resembles “admarat”", "الآخر يشبه «أضمرت»"),
    ("ending tentatively “barakhu”", "الآخر باحتمال «برخ»"),
    ("ending tentatively “qad 'alat”", "الآخر باحتمال «قد علت»"),
    ("final word resembles “an-nut”", "الكلمة الأخيرة تشبه «النوت»"),
    ("final word resembles “tasamat”", "الكلمة الأخيرة تشبه «تسمت»"),
    ("following fragment resembles “labahram”", "الشظية التالية تشبه «لبهرم»"),
    ("following name resembles “wayishrah”", "الاسم التالي يشبه «ويشره»"),
    ("following word resembles “a'zham”", "الكلمة التالية تشبه «أعظم»"),
    ("following word resembles “an-nadhkh/an-nafih”", "الكلمة التالية تشبه «النذخ/النفخ»"),
    ("following word resembles “kawn”", "الكلمة التالية تشبه «كون»"),
    ("following word resembles “rasluha”", "الكلمة التالية تشبه «راسلها»"),
    ("following word resembles “sarabahu”", "الكلمة التالية تشبه «سربه»"),
    ("following word resembles “yanshukh”", "الكلمة التالية تشبه «ينشخ»"),
    ("verb resembles “nafarat”", "الفعل يشبه «نفرت»"),
    ("word resembles “'azhim”", "الكلمة تشبه «عظيم»"),
    ("word resembles “abrasham”", "الكلمة تشبه «أبرشم»"),
    ("word resembles “arbat”", "الكلمة تشبه «أربت»"),
    ("word resembles “shamsayn”", "الكلمة تشبه «شمسين»"),
    ("the next form resembles barikh", "الصيغة التالية تشبه «برخ»"),
    ("the next printed word appears to be “anta”", "الكلمة المطبوعة التالية تبدو «أنت»"),
    ("middle word appears to be “qawiyy”", "الكلمة الوسطى تبدو «قويّ»"),
    ("the word begins “kafana/kafayna”", "الكلمة تبدأ بـ«كفنا/كفينا»"),
    ("remaining strokes resemble “tashakhkhasat”; tentative",
     "الآثار الباقية تشبه «تشخصت» باحتمال"),
    ("the following word is unclear; its letters resemble “an-nafih/an-nafij”",
     "الكلمة التالية غير واضحة، وحروفها تشبه «النفخ/النفج»"),
    ("the fragments “'ayn” and “mim” are visible; the rest is unclear",
     "تظهر شظيتا «عين» و«ميم»، والباقي غير واضح"),
    ("two names appear as “ahil” and “shala'", "يظهر الاسمان «أهل» و«شلع»"),
    ("two fragments unclear", "شظيتان غير واضحتين"),
    ("two printed fragments after fa are unclear", "شظيتان مطبوعتان بعد الفاء غير واضحتين"),
    ("two following words unclear; resemble “yaskhan wa-'abduh”",
     "الكلمتان التاليتان غير واضحتين وتشبهان «يسخن وعبدُه»"),
    ("word after khayr unclear", "الكلمة بعد «خير» غير واضحة"),
    ("word after the name unclear", "الكلمة بعد الاسم غير واضحة"),
    ("the words after the vocative are obscured", "الكلمات بعد النداء مطموسة"),
    ("vocative name unclear; final letters resemble “arnakht”",
     "اسم النداء غير واضح، وحروفه الأخيرة تشبه «أرنخت»"),
    ("talismanic word read tentatively as “thabarat”; middle letters unclear",
     "كلمة طلسمية تُقرأ باحتمال «ثبرت»، وحروفها الوسطى غير واضحة"),
    ("the printed ending resembles “qadarat”; reading is tentative",
     "الآخر المطبوع يشبه «قدرت»، والقراءة محتملة"),
    ("the final printed word appears to be sanaya; its vowel pattern is tentative",
     "الكلمة المطبوعة الأخيرة تبدو «سنيا»، وضبط حركاتها محتمل"),
    ("the final printed word is faint; it resembles “bishatat”",
     "الكلمة المطبوعة الأخيرة باهتة وتشبه «بشطط»"),
    ("the final phrase is visible; the middle word is obscured",
     "العبارة الأخيرة ظاهرة، والكلمة الوسطى مطموسة"),
    ("description/ending unclear; final fragment resembles “injalat”",
     "الوصف/الآخر غير واضح، والشظية الأخيرة تشبه «انجلت»"),
    ("after “nasaba hamim,” the phrase is unclear; “jannata al-'awn” and an ending resembling “tanṭamat” are visible",
     "بعد «نصب حميم» العبارة غير واضحة؛ ويظهر «جنة العون» وآخر يشبه «تنطمت»"),
    ("a short printed fragment after al-Injil is unclear",
     "شظية مطبوعة قصيرة بعد «الإنجيل» غير واضحة"),
    ("a short closing fragment is obscured", "شظية ختامية قصيرة مطموسة"),
    ("a short ending is obscured", "آخر قصير مطموس"),

    # --- kalimat/frasa/fi'il cetakan yang dipertahankan ---
    ("the printed phrase is retained; its grammatical connection is unclear",
     "العبارة المطبوعة محفوظة، وصلها النحوي غير واضح"),
    ("the printed phrase is retained; the intended object is unclear",
     "العبارة المطبوعة محفوظة، والمفعول المقصود غير واضح"),
    ("the printed phrase is retained; agreement is unusual",
     "العبارة المطبوعة محفوظة، والمطابقة غير مألوفة"),
    ("the printed phrase is retained despite unusual wording",
     "العبارة المطبوعة محفوظة مع غرابة اللفظ"),
    ("the printed verb is retained; syntax is uncertain",
     "الفعل المطبوع محفوظ، وإعرابه غير محقق"),
    ("the printed verb is retained; its attachment is unclear",
     "الفعل المطبوع محفوظ، ووصله غير واضح"),
    ("the printed verb is retained; its relation to the phrase is uncertain",
     "الفعل المطبوع محفوظ، وعلاقته بالعبارة غير محققة"),
    ("the printed verb is retained; its subject and relation to “hizbi” are uncertain",
     "الفعل المطبوع محفوظ، وفاعله وعلاقته بـ«حزبي» غير محققين"),
    ("the printed verb is retained; its subject is unstated",
     "الفعل المطبوع محفوظ، وفاعله غير مذكور"),
    ("the printed verb is retained; its vocalization is uncertain",
     "الفعل المطبوع محفوظ، وضبطه غير محقق"),
    ("the printed verb is read tentatively; its contextual meaning is unclear",
     "الفعل المطبوع مقروء باحتمال، ومعناه السياقي غير واضح"),
    ("the printed syntax and verb are retained; the referent is unclear",
     "التركيب والفعل المطبوعان محفوظان، والمرجع غير واضح"),
    ("the printed syntax is retained; the clause relation is unclear",
     "التركيب المطبوع محفوظ، وعلاقة الجملة غير واضحة"),
    ("the printed construction is retained; its attachment is unclear",
     "التركيب المطبوع محفوظ، ووصله غير واضح"),
    ("the printed form is retained; its syntax is uncertain",
     "الصيغة المطبوعة محفوظة، وإعرابها غير محقق"),
    ("the printed form is retained; the sentence structure is unclear",
     "الصيغة المطبوعة محفوظة، وتركيب الجملة غير واضح"),
    ("the printed fragments are retained; the connector is illegible",
     "الشظايا المطبوعة محفوظة، والرابط غير مقروء"),
    ("the printed noun “as-saharat” is retained; its sense is uncertain",
     "الاسم المطبوع «السحرة» محفوظ، ومعناه غير محقق"),
    ("the printed word “sur” is retained; its sense in context is uncertain",
     "الكلمة المطبوعة «سور» محفوظة، ومعناها في السياق غير محقق"),
    ("the printed word order is retained; the grammatical relation is unclear",
     "ترتيب الكلمات المطبوع محفوظ، والعلاقة النحوية غير واضحة"),
    ("the printed wording is retained; the referent of “man” is unclear",
     "اللفظ المطبوع محفوظ، ومرجع «من» غير واضح"),
    ("the printed wording is retained; the syntax is unusual",
     "اللفظ المطبوع محفوظ، والإعراب غير مألوف"),
    ("the repeated form follows the print; syntax is uncertain",
     "الصيغة المكررة تابعة للمطبوع، وإعرابها غير محقق"),
    ("unusual printed sequence retained without emendation",
     "ترتيب مطبوع غير مألوف، محفوظ بلا تصحيح"),
    ("irregular printed form retained without emendation",
     "صيغة مطبوعة غير منتظمة، محفوظة بلا تصحيح"),
    ("irregular printed letter sequence retained without emendation",
     "تسلسل حروف مطبوع غير منتظم، محفوظ بلا تصحيح"),
    ("irregular printed sequence retained without emendation",
     "تسلسل مطبوع غير منتظم، محفوظ بلا تصحيح"),
    ("the print reads ma; it is not silently changed to man",
     "المطبوع «ما»، ولم يُغيَّر صامتًا إلى «من»"),
    ("the sequence follows the visible letters; its syntax is not forced",
     "التسلسل تابع للحروف الظاهرة، وإعرابه غير متكلف"),
    ("the conclusion follows the print; syntax is not forced",
     "الخاتمة تابعة للمطبوع، وإعرابها غير متكلف"),
    ("names and final verb follow the visible consonants; no silent normalization",
     "الأسماء والفعل الأخير تتبع الحروف الظاهرة، بلا تسوية صامتة"),
    ("the name and phrase follow the print; the full sense is uncertain",
     "الاسم والعبارة تبعان للمطبوع، والمعنى الكامل غير محقق"),

    # --- yang "visible/terlihat" ---
    ("the visible phrase is retained; final reading remains uncertain",
     "العبارة الظاهرة محفوظة، والقراءة الأخيرة غير محققة"),
    ("the visible phrase is retained; opening reading is uncertain",
     "العبارة الظاهرة محفوظة، وقراءة الافتتاح غير محققة"),
    ("the visible phrase is retained; the line opening is obscured",
     "العبارة الظاهرة محفوظة، وأول السطر مطموس"),
    ("the visible phrase is retained; the opening name is obscured",
     "العبارة الظاهرة محفوظة، واسم الافتتاح مطموس"),
    ("the visible invocation is retained; opening is obscured",
     "الدعاء الظاهر محفوظ، والافتتاح مطموس"),
    ("the visible invocation is retained; the opening name is unreadable",
     "الدعاء الظاهر محفوظ، واسم الافتتاح غير مقروء"),
    ("the visible wording is retained; the middle reading is uncertain",
     "اللفظ الظاهر محفوظ، والقراءة الوسطى غير محققة"),
    ("the visible words are retained; the name fragments are uncertain",
     "الكلمات الظاهرة محفوظة، وشظايا الاسم غير محققة"),
    ("the two visible epithets are retained; the line opening is obscured",
     "النعتان الظاهران محفوظان، وأول السطر مطموس"),
    ("the latter phrase is retained; opening name is obscured",
     "العبارة الأخيرة محفوظة، واسم الافتتاح مطموس"),
    ("the two forms after al are uncertain proper-name readings",
     "الصيغتان بعد «ال» قراءتان غير محققتين لاسم علم"),
    ("the final verb is a tentative reading", "الفعل الأخير قراءة محتملة"),
    ("the final verb is read tentatively from the print",
     "الفعل الأخير مقروء من المطبوع باحتمال"),
    ("the final verb is read tentatively", "الفعل الأخير مقروء باحتمال"),
    ("the final verb is tentative.", "الفعل الأخير محتمل"),
    ("the final verb is tentative", "الفعل الأخير محتمل"),
    ("the final verb resembles “tashalakhat”; tentative",
     "الفعل الأخير يشبه «تشلخت» باحتمال"),
    ("the final words are tentative readings of the print",
     "الكلمات الأخيرة قراءات محتملة للمطبوع"),
    ("the final word resembles “wa-anti”", "الكلمة الأخيرة تشبه «وأنتِ»"),
    ("the opening word is a tentative reading", "أول الكلمة قراءة محتملة"),
    ("the ending is obscured; the verb is tentative", "الآخر مطموس، والفعل محتمل"),
    ("mushriqatan follows the visible print tentatively", "«مشرقة» تتبع المطبوع الظاهر باحتمال"),
    ("katabat is a tentative reading of the final verb", "«كتبت» قراءة محتملة للفعل الأخير"),
    ("tanaffasat is a tentative reading of the visible ending",
     "«تنفست» قراءة محتملة للآخر الظاهر"),
    ("tanaṭṭaqat follows the printed consonants; emphatic ṭā' is doubled",
     "«تنطّقت» تتبع حروف المطبوع، والطاء المهملة مشددة"),
    ("ahriq is read as an imperative in this supplication; the print has no vowel marks",
     "«أحرق» يُقرأ فعل أمر في هذا الدعاء، والمطبوع بلا حركات"),
    ("Ghalawun is retained as a proper name; its vowel pattern is editorial",
     "«غلون» محفوظ اسم علم، وضبط حركاته اجتهادي"),
    ("Mandarish is a proper name; the final phrase follows the printed letters",
     "«مندرش» اسم علم، والعبارة الأخيرة تابعة لحروف المطبوع"),
    ("Marza'il is a proper name; its vowels are editorial",
     "«مرزائيل» اسم علم، وحركاته اجتهادية"),
    ("Anwakh is a tentative reading of the printed proper name",
     "«أنوخ» قراءة محتملة للاسم العلم المطبوع"),
    ("Ankh is a proper-name reading; the ending is unclear",
     "«أنخ» قراءة اسم علم، وآخره غير واضح"),
    ("Amuj and Jalilat are tentative readings of proper names",
     "«أموج» و«جليلات» قراءتان محتملتان لاسمين علمين"),
    ("Both names are approximate readings of the printed forms",
     "الاسمان قراءتان تقريبيتان للصيغتين المطبوعتين"),
    ("Both names are tentative readings of the printed forms",
     "الاسمان قراءتان محتملتان للصيغتين المطبوعتين"),
    ("The two names are read tentatively from print",
     "الاسمان مقروءان من المطبوع باحتمال"),
    ("The printed name is repeated; vowels are approximate",
     "الاسم المطبوع مكرر، وحركاته تقريبية"),
    ("The name is tentatively read from the print; ahraqtu is first-person active",
     "الاسم مقروء من المطبوع باحتمال، و«أحرقتُ» مبني للمعلوم للمتكلم"),
    ("Ṭarum is a tentative reading of the non-Arabic name after “might”",
     "«طارم» قراءة محتملة للاسم غير العربي بعد «العزة»"),
    ("“Thuran” and the final phrase are tentative readings of the print",
     "«ثوران» والعبارة الأخيرة قراءتان محتملتان للمطبوع"),
    ("“azmi qawiyyun” is visible; the surrounding words are uncertain",
     "يظهر «عزم قوي»، والكلمات المحيطة غير محققة"),
    ("a line of connected talismanic names; the letter sequence is too indistinct for a reliable phonetic rendering",
     "سطر من أسماء طلسمية متصلة، وتسلسل حروفه غير متمايز بما لا يسمح بنقل صوتي موثوق"),
    ("A line of talismanic names; connected letters are too indistinct for a safe phonetic transcription",
     "سطر من أسماء طلسمية، وحروفه المتصلة غير متمايزة بما لا يسمح بنقل صوتي موثوق"),
    ("line of talismanic names; the ending only tentatively resembles “ash-shadhikh” and “banukh”",
     "سطر من أسماء طلسمية، وآخره يشبه باحتمال «الشذيخ» و«بنوخ»"),
    ("connected talismanic names; middle letters cannot be read confidently",
     "أسماء طلسمية متصلة، وحروفها الوسطى لا تُقرأ بثقة"),
    ("proper names and the middle form are tentative readings",
     "الأسماء العلم والصيغة الوسطى قراءات محتملة"),

    # --- catatan al-matbu' panjang (nahwu/tajwid) ---
    ("al-matbu': ahrqt without vowels; read ahraqtu (active first-person); al-jinna is fronted object; tajwid: qalqalah sughra on sakin qaf, ghunnah on mushaddad nun in al-jinn",
     "المطبوع: «أحرقت» بلا حركات؛ تُقرأ «أحرقتُ» (مبني للمعلوم للمتكلم)، و«الجنّ» مفعول مقدم؛ تجويد: قلقلة صغرى في القاف الساكنة، وغنة في النون المشددة من «الجنّ»"),
    ("al-matbu': anzalt without vowels; preferred active anzaltu with zalazila as fronted object; passive unzilat would require nominative zalazilu; tajwid: ikhfa before zay, izhar of tanwin before hamza, ghunnah on mushaddad nun in al-jinn",
     "المطبوع: «أنزلت» بلا حركات؛ الأرجح «أنزلتُ» مبنيًا للمعلوم و«زلزلة» مفعول مقدم؛ ولو كان «أُنزلت» مبنيًا للمجهول لوجب رفع «زلازل»؛ تجويد: إخفاء قبل الزاي، وإظهار للتنوين قبل الهمزة، وغنة في النون المشددة من «الجنّ»"),
    ("al-matbu': banat; al-qira'ah al-muqtarahah: kasabat, per parallel Qur'anic al-Muddaththir 74:38; kullu nafsin fa'il tajzi, feminine pronoun in kasabat refers to nafs; tajwid: tanwin nafsin before ba is iqlab with ghunnah",
     "المطبوع: «بنت»؛ القراءة المقترحة: «كسبت» نظير قوله تعالى في المدثر ٧٤:٣٨؛ و«كل نفس» فاعل «تجزي»، والضمير المؤنث في «كسبت» يعود إلى «نفس»؛ تجويد: تنوين «نفسٍ» قبل الباء إقلاب مع غنة"),
    ("al-matbu': lil-fasahati; kept without emendation absent decisive witness; wasl: balagh and warning after punishment; nahw: hadha mubtada', balagh khabar, li-yundharu passive subjunctive, waw na'ib fa'il; tajwid: nun sakinah before dhal is ikhfa haqiqi with ghunnah",
     "المطبوع: «للفصاحة»؛ محفوظ بلا تصحيح لعدم وجود شاهد قاطع؛ وصل: بلاغ وتحذير بعد العقاب؛ نحو: «هذا» مبتدأ و«بلاغ» خبر، و«لينذر» منصوب مبني للمجهول، والواو نائب فاعل؛ تجويد: النون الساكنة قبل الذال إخفاء حقيقي مع غنة"),
    ("al-matbu': nahimin; dabt ihtimali nahimina, without claiming a definite emendation; wasl: context is 'adhab al-hamim; nahw: probable hal mansub referring to the plural pronoun; tajwid: ha' is a hams consonant; no sakin qaf or doubled nun here",
     "المطبوع: «ناحمين»؛ ضبط احتمالي «نَاحِمِينَ» بلا جزم بتصحيح؛ وصل: السياق عذاب الحميم؛ نحو: حال منصوب محتمل يرجع إلى ضمير الجمع؛ تجويد: الحاء حرف همس، ولا قاف ساكنة ولا نون مشددة هنا"),
    ("al-matbu': tamahhadat without vowels; tentative active feminine past, explicit subject absent; wasl: after jinn's movement and before request for their subjugation; nahw: feminine past verb, subject not explicit; tajwid: hā' is hams, ṭā' is a solar letter",
     "المطبوع: «تمهدت» بلا حركات؛ ماضٍ مؤنث مبني للمعلوم باحتمال، وفاعله غير مذكور؛ وصل: بعد حركة الجن وقبل طلب تسخيرهم؛ نحو: فعل ماضٍ مؤنث وفاعله غير ظاهر؛ تجويد: الهاء حرف همس، والطاء حرف شمسي"),
    ("al-matbu': tasara'at unvowelled; tentative dabt: tasara'at; wasl: divine might and retribution followed by the sinners; nahw: feminine perfect verb with no explicit subject; tajwid: no sakin qaf or doubled nun in this word",
     "المطبوع: «تسرعت» بلا حركات؛ ضبط احتمالي «تسارعت»؛ وصل: قدرة إلهية وانتقام تليه المجرمون؛ نحو: فعل ماضٍ مؤنث بلا فاعل ظاهر؛ تجويد: لا قاف ساكنة ولا نون مشددة في هذه الكلمة"),
]

# Catatan khusus halaman cetak 4 (PDF 5): emendasi nahwu & falak.
PETA.append((
    "the printed phrase “ayyu maa daraa” is retained; its construction is unclear",
    "في المطبوع «أي ما درى» وهو محرف، وصوابه على مقتضى النحو والفلك «وَأَيْنَمَا دَارَ» "
    "أي حيثما دار الفلك في برجه — dimanapun beredar",
))

# ---------------------------------------------------------------------------
# 2. Emendasi nahwu & falak (hal. cetak 4) — teks cetak tetap dicatat.
# ---------------------------------------------------------------------------

EMENDASI: list[tuple[str, str]] = [
    (
        "وأيما دار ما درى [الصيغة كما في المطبوع مع غرابة تركيبها؛ لا تُصحح بلا شاهد أوضح]",
        "وَأَيْنَمَا دَارَ [في المطبوع «أيما دار ما درى» وهو محرَّف؛ وصوابه على مقتضى النحو والفلك "
        "«وَأَيْنَمَا دَارَ» أي حيثما دار الفلك في برجه]",
    ),
    (
        "Wa ayyumaa daara maa daraa [the printed phrase “ayyu maa daraa” is retained; its construction is unclear]",
        "Wa aynamaa daara [في المطبوع «أي ما درى» وهو محرف، وصوابه على مقتضى النحو والفلك "
        "«وَأَيْنَمَا دَارَ» أي حيثما دار الفلك في برجه — dimanapun beredar]",
    ),
    (
        # perbaikan bila catatan sudah sempat diganti Arab (idempoten):
        "Wa ayyumaa daara maa daraa [في المطبوع",
        "Wa aynamaa daara [في المطبوع",
    ),
    # penyelaras kalimat baku phonetic (idempoten):
    (
        "القراءة محتملة، والحروف محفوظة وفق الطباعة",
        "القراءة محتملة، والحروف محفوظة على رسم المطبوع - qiraatuhu muhtamalah",
    ),
    (
        "قراءة الاسم غير العربي محتملة، وحروفه محفوظة وفق الطباعة",
        "القراءة محتملة، والحروف محفوظة على رسم المطبوع - qiraatuhu muhtamalah",
    ),
    (
        "الاسم غير العربي محتمل، والحروف المطبوعة محفوظة",
        "القراءة محتملة، والحروف محفوظة على رسم المطبوع - qiraatuhu muhtamalah",
    ),
    (
        "اسم «ليشيشو» محتمل، والحروف المطبوعة محفوظة",
        "اسم «ليشيشو» محتمل، والحروف محفوظة على رسم المطبوع",
    ),
    (
        "Dan [kalimat «wa ayyumaa daara maa daraa» tidak jelas, tampaknya rusak dalam cetakan]; bila",
        "Dan «dimanapun beredar» (yakni di manapun benda langit itu beredar pada burujnya); bila",
    ),
    (
        "Kalimat «وأيما دار ما درى» tampak rusak dalam cetakan sehingga dibiarkan tanpa harakat dan "
        "ditandai [الصيغة كما في المطبوع مع غرابة تركيبها؛ لا تُصحح بلا شاهد أوضح]; arti umum kalimat sesudahnya:",
        "Kalimat «أيما دار ما درى» pada cetakan tampak salah tulis (محرَّف); atas pertimbangan nahwu dan falak "
        "dibaca «وَأَيْنَمَا دَارَ» — «dimanapun beredar» (yakni di manapun benda langit itu beredar pada "
        "burujnya), dan bentuk cetaknya tetap dicatat; arti umum kalimat sesudahnya:",
    ),
]

# ---------------------------------------------------------------------------
# Mesin pengganti
# ---------------------------------------------------------------------------

CATATAN = re.compile(r"\[[^\]\n]{1,400}\]")
TANDA_INGGRIS = re.compile(
    r"\b(the|this|that|these|those|its|is|are|was|were|been|being|with|without|and|or|of|to|"
    r"from|for|in|on|at|by|as|after|before|between|both|two|no|not|kept|retained|unclear|"
    r"unreadable|obscured|tentative|uncertain|indistinct|illegible|emendation|syntax|vowel|"
    r"vowels|pronoun|verb|noun|phrase|clause|fragment|fragments|visible|printed|print|reading|"
    r"follows|resembles|silent|editorial|proper|talismanic|vocative|stroke|strokes|token|tokens|"
    r"approximate|unvowelled|appears|appear|may|might|cannot|too|following|line|lines|word|words|"
    r"letter|letters|form|forms|ending|opening|middle|final|first|second|kept|read|reads|spelled|"
    r"normalization|emendation|number|numbers|column|columns|verse|verses|name|names)\b",
    re.IGNORECASE,
)


def kanon(teks: str) -> str:
    """Bentuk banding: tanpa kurung, kutip melengkung disamakan, huruf kecil, spasi rapat."""
    s = teks.strip().strip("[]").strip()
    for a, b in [
        ("“", '"'), ("”", '"'), ("‘", "'"), ("’", "'"), ("–", "-"), ("—", "-"),
        ("ṭ", "t"), ("ā", "a"), ("ī", "i"), ("ū", "u"), ("ṣ", "s"), ("ḍ", "d"),
        ("ḥ", "h"), ("ẓ", "z"), ("Ṭ", "T"),
    ]:
        s = s.replace(a, b)
    s = re.sub(r"\s+", " ", s).strip().rstrip(".").strip()
    return s.lower()


PETA_KANON = {kanon(k): v for k, v in PETA}


def normalisasi(teks: str) -> tuple[str, int]:
    """Terapkan emendasi nahwu/falak lebih dulu, lalu ganti catatan Inggris -> Arab."""
    jumlah = 0

    for lama, baru in EMENDASI:
        if lama in teks:
            jumlah += 1
            teks = teks.replace(lama, baru)

    def ganti(m: re.Match) -> str:
        nonlocal jumlah
        arab = PETA_KANON.get(kanon(m.group(0)))
        if arab is None:
            return m.group(0)
        jumlah += 1
        return f"[{arab}]"

    teks = CATATAN.sub(ganti, teks)
    return teks, jumlah


BERKAS_SASARAN = ("BATCH_*.md", "KAMUS_*.md")


def berkas_sumber(akar: Path) -> list[Path]:
    hasil: list[Path] = []
    for pola in BERKAS_SASARAN:
        hasil.extend(sorted(akar.glob(pola)))
    return hasil


def sisa_inggris(akar: Path) -> list[str]:
    temuan: list[str] = []
    # Catatan berbahasa Indonesia (bukan Inggris) yang memuat nama Latin, dikecualikan.
    pengecualian = {"[tercetak: al-Mugh'its]"}
    for f in berkas_sumber(akar):
        for ln, baris in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for m in CATATAN.finditer(baris):
                s = m.group(0)
                if re.search(r"[\u0600-\u06FF]", s) or s in pengecualian:
                    continue
                if s in ("[Teks Arab Asli]", "[Transliterasi Latin Fonetik]", "[Terjemahan Indonesia]",
                         "[Syarah]", "[Faedah]") or s.startswith("[Rajah") or s.startswith("[Gambar"):
                    continue
                if TANDA_INGGRIS.search(s):
                    temuan.append(f"{f.name}:{ln}: {s[:180]}")
    return temuan


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Normalisasi catatan Inggris -> Arab + emendasi nahwu/falak hal 4")
    ap.add_argument("--cek", "--check-only", action="store_true", help="hanya periksa (jangan ubah berkas)")
    ap.add_argument("--akar", default=str(ROOT))
    args = ap.parse_args(argv)
    akar = Path(args.akar)

    if args.cek:
        temuan = sisa_inggris(akar)
        print(f"PEMERIKSAAN catatan Inggris: {'BERSIH (0)' if not temuan else str(len(temuan)) + ' sisa'}")
        for t in temuan:
            print("  ", t)
        return 1 if temuan else 0

    total = 0
    for f in berkas_sumber(akar):
        lama = f.read_text(encoding="utf-8")
        baru, n = normalisasi(lama)
        if n:
            f.write_text(baru, encoding="utf-8")
            total += n
            print(f"  {f.name}: {n} catatan")
    print(f"selesai: {total} penggantian")
    sisa = sisa_inggris(akar)
    print(f"sisa Inggris: {len(sisa)}")
    for t in sisa:
        print("  ", t)
    return 1 if sisa else 0


if __name__ == "__main__":
    sys.exit(main())
