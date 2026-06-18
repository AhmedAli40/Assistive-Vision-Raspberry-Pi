"""
registration.py — v7
التعديلات:
  1. Beep صوت "تن" كل 3 ثواني أثناء تسجيل الشخص
  2. إرشادات للشخص أثناء التسجيل (انظر يمين، شمال، فوق، غير تعبير وجه...)
  3. كل الجمل مترجمة عربي/إنجليزي حسب config.LANGUAGE
"""

import time, queue, threading, logging, json, os, re
import numpy as np
import config

try:
    import winsound
    _BEEP_OK = True
except ImportError:
    _BEEP_OK = False

logger   = logging.getLogger(__name__)
SAMPLES  = 120   # زدنا من 80 ل→ 120 صورة — تغطية أخسن لتعابير مختلفة
TIMEOUT  = 90.0  # زدنا من 60 ل→ 90 ثانية عشان نكدر نلتقط الصور الكافية

BLOCK_FILE = "blocked.json"

# ── نصوص اللغتين ─────────────────────────────────────────────────────────────
_STR = {
    "en": {
        "say_name":         "Please say the name of this person.",
        "didnt_hear":       "I did not hear you. Please try again.",
        "heard":            "I heard {name}. Is that correct? Say yes or no.",
        "try_again":        "Let us try again.",
        "no_name":          "Could not get a name. Registration cancelled.",
        "registering":      "Registering {name}. Please stand still and face the camera.",
        "vary_expr_hint":   "Tip: slightly vary your expression during capture for better accuracy.",
        "not_enough":       "Not enough photos captured. Please try again.",
        "success":          "{name} has been registered successfully.",
        "no_to_delete":     "No registered persons to delete.",
        "say_delete":       "Registered persons: {names}. Say the name to delete.",
        "no_name_heard":    "No name heard. Cancelled.",
        "not_found":        "Could not find {name}. Cancelled.",
        "confirm_delete":   "Delete {name}? Say yes or no.",
        "cancelled":        "Cancelled.",
        "deleted":          "{name} has been deleted.",
        "keep_person":      "Please keep the person in front of the camera.",
        "no_frame":         "No image received. Cancelling.",
        "no_face":          "No face detected. Please stand in front of the camera.",
        "already_reg":      "This person is already registered as {name}. Cannot block a registered person.",
        "say_label":        "Say a label for this person.",
        "no_label":         "No label heard. Cancelling.",
        "blocking":         "Blocking {name}. Please stay still.",
        "blocked":          "{name} has been blocked.",
        "no_blocked":       "No blocked persons.",
        "say_unblock":      "Blocked persons: {names}. Say the name to unblock.",
        "not_blocked":      "Could not find {name} in the blocked list.",
        "confirm_unblock":  "Unblock {name}? Say yes or no.",
        "unblocked":        "{name} has been unblocked.",
        "look_straight":    "Please look straight at the camera.",
        "look_left":        "Please turn your head slightly to the left.",
        "look_right":       "Please turn your head slightly to the right.",
        "vary_expression":  "Now, smile or change your expression.",
    },
    "ar": {
        "say_name":         "من فضلك قل اسم هذا الشخص.",
        "didnt_hear":       "لم أسمعك. من فضلك حاول مرة أخرى.",
        "heard":            "سمعت {name}. هل هذا صحيح؟ قل نعم أو لا.",
        "try_again":        "لنحاول مرة أخرى.",
        "no_name":          "لم أتمكن من الحصول على اسم. تم إلغاء التسجيل.",
        "registering":      "جاري تسجيل {name}. من فضلك قف أمام الكاميرا بثبات.",
        "vary_expr_hint":   "نصيحة: غيّر تعبيرك قليلاً أثناء التسجيل لدقة أعلى.",
        "not_enough":       "لم يتم التقاط صور كافية. من فضلك حاول مرة أخرى.",
        "success":          "تم تسجيل {name} بنجاح.",
        "no_to_delete":     "لا يوجد أشخاص مسجلون للحذف.",
        "say_delete":       "الأشخاص المسجلون: {names}. قل الاسم الذي تريد حذفه.",
        "no_name_heard":    "لم أسمع اسماً. تم الإلغاء.",
        "not_found":        "لم أجد {name}. تم الإلغاء.",
        "confirm_delete":   "هل تريد حذف {name}؟ قل نعم أو لا.",
        "cancelled":        "تم الإلغاء.",
        "deleted":          "تم حذف {name}.",
        "keep_person":      "من فضلك ابق الشخص أمام الكاميرا.",
        "no_frame":         "لم يصل أي إطار. جاري الإلغاء.",
        "no_face":          "لم يتم اكتشاف وجه. من فضلك قف أمام الكاميرا.",
        "already_reg":      "هذا الشخص مسجل بالفعل باسم {name}. لا يمكن حظر شخص مسجل.",
        "say_label":        "قل تسمية لهذا الشخص.",
        "no_label":         "لم أسمع تسمية. جاري الإلغاء.",
        "blocking":         "جاري حظر {name}. ابق ثابتاً من فضلك.",
        "blocked":          "تم حظر {name}.",
        "no_blocked":       "لا يوجد أشخاص محظورون.",
        "say_unblock":      "الأشخاص المحظورون: {names}. قل الاسم الذي تريد رفع حظره.",
        "not_blocked":      "لم أجد {name} في قائمة الحظر.",
        "confirm_unblock":  "هل تريد رفع حظر {name}؟ قل نعم أو لا.",
        "unblocked":        "تم رفع حظر {name}.",
        "look_straight":    "من فضلك انظر مباشرة إلى الكاميرا.",
        "look_left":        "من فضلك التفت برأسك قليلاً إلى اليسار.",
        "look_right":       "من فضلك التفت برأسك قليلاً إلى اليمين.",
        "vary_expression":  "الآن، ابتسم أو غير تعبير وجهك.",
    },
}

_STR["en"].update({
    "improve_who": "Which registered person do you want to improve?",
    "confirm_improve": "Improve {name}? Say yes or no.",
    "improving": "Improving {name}. Please face the camera and follow the guidance.",
    "improved": "{name} has been improved successfully.",
    "no_registered": "No registered persons.",
})
_STR["ar"].update({
    "improve_who": "\u0645\u0646 \u0627\u0644\u0634\u062e\u0635 \u0627\u0644\u0645\u0633\u062c\u0644 \u0627\u0644\u0630\u064a \u062a\u0631\u064a\u062f \u062a\u062d\u0633\u064a\u0646\u0647\u061f",
    "confirm_improve": "\u0647\u0644 \u062a\u0631\u064a\u062f \u062a\u062d\u0633\u064a\u0646 \u062a\u0633\u062c\u064a\u0644 {name}\u061f \u0642\u0644 \u0646\u0639\u0645 \u0623\u0648 \u0644\u0627.",
    "improving": "\u062c\u0627\u0631\u064a \u062a\u062d\u0633\u064a\u0646 \u062a\u0633\u062c\u064a\u0644 {name}. \u0645\u0646 \u0641\u0636\u0644\u0643 \u0648\u0627\u062c\u0647 \u0627\u0644\u0643\u0627\u0645\u064a\u0631\u0627 \u0648\u0627\u062a\u0628\u0639 \u0627\u0644\u0625\u0631\u0634\u0627\u062f\u0627\u062a.",
    "improved": "\u062a\u0645 \u062a\u062d\u0633\u064a\u0646 \u062a\u0633\u062c\u064a\u0644 {name} \u0628\u0646\u062c\u0627\u062d.",
    "no_registered": "\u0644\u0627 \u064a\u0648\u062c\u062f \u0623\u0634\u062e\u0627\u0635 \u0645\u0633\u062c\u0644\u0648\u0646.",
})


def _t(key: str, **kwargs) -> str:
    lang = getattr(config, "LANGUAGE", "en")
    text = _STR.get(lang, _STR["en"]).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text


import sys as _sys
import subprocess as _subprocess


def _beep():
    """صوت تن قصير يعلم الشخص بالتقاط صورة."""
    if _BEEP_OK:
        try:
            winsound.Beep(1000, 70)
            return
        except Exception:
            pass
    # Linux / Raspberry Pi fallback
    if _sys.platform != 'win32':
        try:
            # Generate a short beep tone using aplay (available on most RPi setups)
            _subprocess.Popen(
                ['python3', '-c',
                 'import struct,wave,os,tempfile;'
                 'f=tempfile.NamedTemporaryFile(suffix=".wav",delete=False);'
                 'w=wave.open(f.name,"w");w.setnchannels(1);w.setsampwidth(2);'
                 'w.setframerate(16000);'
                 'd=b"".join(struct.pack("<h",int(20000*__import__("math").sin(2*3.14159*1000*i/16000))) for i in range(1920));'
                 'w.writeframes(d);w.close();'
                 'os.system("aplay -q "+f.name);os.unlink(f.name)'],
                stdout=_subprocess.DEVNULL,
                stderr=_subprocess.DEVNULL,
            )
            return
        except Exception:
            pass
    print("\a", end="", flush=True)


def _beep_beep():
    """صوت تن تن قصير (مزدوج) يعلم المستخدم أن النظام يعمل بنشاط."""
    if _BEEP_OK:
        def _play():
            try:
                winsound.Beep(1200, 80)
                time.sleep(0.1)
                winsound.Beep(1200, 80)
            except Exception:
                pass
        threading.Thread(target=_play, daemon=True).start()
        return
    # Linux / Raspberry Pi fallback — two short beeps
    if _sys.platform != 'win32':
        def _play_linux():
            _beep()
            time.sleep(0.15)
            _beep()
        threading.Thread(target=_play_linux, daemon=True).start()
        return
    # fallback
    print("\a\a", end="", flush=True)


def load_blocked() -> set:
    if os.path.exists(BLOCK_FILE):
        try:
            with open(BLOCK_FILE) as f:
                return set(json.load(f))
        except Exception:
            pass
    return set()


def save_blocked(blocked: set):
    with open(BLOCK_FILE, "w") as f:
        json.dump(list(blocked), f)


# ─────────────────────────────────────────────────────────────────────────────

try:
    from shared.tts import TTS
    from shared.stt import STT
    from face.face_db import FaceDB
    from face.face_processor import FaceProcessor
except ImportError:
    from tts import TTS
    from stt import STT
    from face_db import FaceDB
    from face_processor import FaceProcessor


def _parse_number(text: str) -> int | None:
    t = _normalize_command_text(text)
    if t.isdigit():
        return int(t)
    
    eng_map = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
    ar_map = {
        "واحد": 1, "واحدة": 1, "اتنين": 2, "اثنين": 2, "تلاتة": 3, "ثلاثة": 3, "تلاته": 3, "ثلاثه": 3,
        "اربعة": 4, "أربعة": 4, "اربع": 4, "خمسة": 5, "خمسه": 5, "خمس": 5, "ستة": 6, "سته": 6, "ست": 6,
        "سبعة": 7, "سبعه": 7, "سبع": 7, "ثمانية": 8, "تمانية": 8, "تمانيه": 8, "تسعة": 9, "تسعه": 9, "عشرة": 10, "عشره": 10
    }
    
    number_prefixes = (
        "number", "number.", "no", "no.", "num", "num.",
        "رقم", "نمبر", "نمرة", "رقم الشخص", "الشخص رقم",
    )
    for prefix in number_prefixes:
        if t.startswith(prefix + " "):
            t = t[len(prefix):].strip()
            break

    digit_match = re.search(r"\d+", t)
    if digit_match:
        return int(digit_match.group(0))

    if t in eng_map:
        return eng_map[t]
    if t in ar_map:
        return ar_map[t]
        
    for word, val in eng_map.items():
        if word in t:
            return val
    for word, val in ar_map.items():
        if word in t:
            return val
    return None


def _normalize_command_text(text: str) -> str:
    t = str(text or "").strip().lower()
    arabic_digits = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
    eastern_digits = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
    t = t.translate(arabic_digits).translate(eastern_digits)
    t = re.sub(r"[^\w\s\u0600-\u06ff]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def _is_delete_all_command(text: str) -> bool:
    t = _normalize_command_text(text)
    if not t:
        return False

    exact = {
        "all", "all names", "delete all", "delete everyone", "everyone",
        "everybody", "whole list", "clear all", "wipe all", "remove all",
        "all people", "all persons",
        "الكل", "كل", "كله", "كلهم", "امسح الكل", "احذف الكل",
        "حذف الكل", "مسح الكل", "كل الاسماء", "كل الأسماء",
        "جميع الاسماء", "جميع الأسماء", "كل الناس", "الجميع",
    }
    if t in exact:
        return True

    # Common STT near-misses for "all"; keep these scoped to delete flow only.
    near_misses = {"old", "ole", "owl", "call"}
    if t in near_misses:
        return True

    return (
        ("all" in t and any(w in t for w in ("delete", "clear", "wipe", "remove", "names", "people")))
        or ("كل" in t and any(w in t for w in ("امسح", "احذف", "حذف", "مسح", "اسم", "الاسماء", "الأسماء")))
    )


class RegFlow:
    def __init__(self, tts: TTS, stt: STT, db: FaceDB, proc: FaceProcessor):
        self.tts     = tts
        self.stt     = stt
        self.db      = db
        self.proc    = proc
        self.blocked = load_blocked()

        self._fq     = queue.Queue(maxsize=3)
        self._rq     = queue.Queue(maxsize=1)
        self._active = False
        self._mode   = "register"
        self._target_name = None
        self.current_instruction = ""

    @property
    def active(self): return self._active

    def start_register(self): self._go("register")
    def start_improve(self, name: str | None = None):
        self._target_name = name
        self._go("improve")
    def start_delete(self):   self._go("delete")
    def start_block(self):    self._go("block")
    def start_unblock(self):  self._go("unblock")

    def _go(self, mode: str):
        deadline = time.time() + 60.0
        while self._active and time.time() < deadline:
            time.sleep(0.2)
        if self._active:
            return
        self._mode   = mode
        self._active = True
        while not self._fq.empty():
            try: self._fq.get_nowait()
            except: pass
        threading.Thread(target=self._run, daemon=True).start()

    def feed(self, frame: np.ndarray):
        if not self._active: return
        if self._fq.full():
            try: self._fq.get_nowait()
            except: pass
        try: self._fq.put_nowait(frame.copy())
        except: pass

    def result(self):
        try:
            r = self._rq.get_nowait()
            self._active = False
            return r
        except queue.Empty:
            return "PENDING"

    def _run(self):
        r = None
        try:
            if   self._mode == "register": r = self._register()
            elif self._mode == "improve":  r = self._improve()
            elif self._mode == "delete":   r = self._delete()
            elif self._mode == "block":    r = self._block()
            elif self._mode == "unblock":  r = self._unblock()
        except Exception as e:
            logger.error(f"RegFlow: {e}", exc_info=True)
        finally:
            self._rq.put(r)
            self._active = False
            self.current_instruction = ""

    # ── Register ──────────────────────────────────────────────────────────────

    def _register(self):
        name = None
        for attempt in range(1, 4):
            self._say(_t("say_name"))
            heard = self.stt.get_name(tries=2, timeout=10.0, tts=self.tts)
            if heard:
                h_cleaned = heard.lower().strip()
                if h_cleaned in ["cancel", "exit", "stop", "close", "الغي", "الغ", "الغاء", "إلغاء", "بلاش", "خروج", "اخرج"]:
                    self._say(_t("cancelled"))
                    return None
            if not heard:
                if attempt < 3:
                    self._say(_t("didnt_hear"))
                continue
            self._say(_t("heard", name=heard))
            ok = self.stt.yes_no(tries=3, timeout=8.0, tts=self.tts)
            if ok is True:
                name = heard
                break
            self._say(_t("try_again"))

        if not name:
            self._say(_t("no_name"))
            return None

        self._say(_t("registering", name=name))
        self._say(_t("vary_expr_hint"))   # نصيحة واحدة فقط عن تنويع التعابير
        embs = self._capture_with_guidance()

        if len(embs) < 15:
            self._say(_t("not_enough"))
            return None

        self.db.add(name, embs)
        self._say(_t("success", name=name))
        return f"registered:{name}"

    def _match_registered_name(self, target: str) -> str | None:
        ns = [n for n in self.db.names() if not n.startswith("__blocked__")]
        if not target:
            return None
        target_l = target.lower().strip()
        return next(
            (n for n in ns if n.lower() == target_l or target_l in n.lower()),
            None
        )

    def _improve(self):
        ns = [n for n in self.db.names() if not n.startswith("__blocked__")]
        if not ns:
            self._say(_t("no_registered"))
            return None

        name = self._match_registered_name(self._target_name or "")
        if not name:
            self._say(_t("improve_who"))
            for attempt in range(1, 4):
                heard = self.stt.get_name(tries=2, timeout=10.0, tts=self.tts)
                if not heard:
                    if attempt < 3:
                        self._say(_t("try_again"))
                    continue
                name = self._match_registered_name(heard)
                if name:
                    break
                self._say(_t("not_found", name=heard))
                if attempt < 3:
                    self._say(_t("try_again"))

        if not name:
            self._say(_t("cancelled"))
            return None

        self._say(_t("confirm_improve", name=name))
        if self.stt.yes_no(tries=4, timeout=8.0, tts=self.tts) is not True:
            self._say(_t("cancelled"))
            return None

        self._say(_t("improving", name=name))
        self._say(_t("vary_expr_hint"))
        embs = self._capture_with_guidance()
        if len(embs) < 10:
            self._say(_t("not_enough"))
            return None

        self.db.add(name, embs)
        self._say(_t("improved", name=name))
        return f"improved:{name}"

    # ── Capture with guidance + beeps ─────────────────────────────────────────

    def _capture_with_guidance(self) -> list:
        """
        يلتقط الصور من زوايا وتعبيرات مختلفة عن طريق توجيه المستخدم صوتياً.
        """
        embs = []
        phase_samples = SAMPLES // 4  # 30 صورة لكل مرحلة
        
        phases = [
            ("straight", _t("look_straight")),
            ("left", _t("look_left")),
            ("right", _t("look_right")),
            ("expression", _t("vary_expression"))
        ]

        for phase_name, instruction in phases:
            self._say(instruction)
            time.sleep(0.25)  # مهلة قصيرة ليستعد المستخدم
            
            phase_captured = 0
            # مهلة أقصاها 20 ثانية لهذه المرحلة
            deadline = time.time() + 20.0
            last_beep_time = time.time()
            last_no_face_prompt = 0.0
            
            while phase_captured < phase_samples and time.time() < deadline:
                now = time.time()
                if now - last_beep_time >= 3.0:
                    _beep()
                    last_beep_time = now

                try:
                    frame = self._fq.get(timeout=0.5)
                except queue.Empty:
                    continue

                faces = self.proc.detect(frame)
                if not faces:
                    now = time.time()
                    if now - last_no_face_prompt >= 6.0:
                        self._say(_t("no_face"))
                        last_no_face_prompt = now
                    continue

                # نقوم بترتيب الوجوه وأخذ الأكبر مساحة (الأقرب للكاميرا) لضمان الدقة
                faces_sorted = sorted(faces, key=lambda b: b[2] * b[3], reverse=True)
                
                e = self.proc.embed(frame, faces_sorted[0])
                if e is not None:
                    embs.append(e)
                    phase_captured += 1
            
            # beep مزدوج في نهاية المرحلة للتقدم
            _beep_beep()
            time.sleep(0.1)

        logger.info(f"Captured {len(embs)} embeddings total.")
        return embs

    # ── Delete ────────────────────────────────────────────────────────────────

    def _delete(self):
        ns = [n for n in self.db.names() if not n.startswith("__blocked__")]
        if not ns:
            self._say(_t("no_to_delete"))
            return None
        
        # قراءة القائمة بالأرقام المترتبة مع خيار الكل
        numbered_list = [f"{i+1} {name}" for i, name in enumerate(ns)]
        is_ar = getattr(config, "LANGUAGE", "en") == "ar"
        if is_ar:
            names_str = "، ".join(numbered_list) + "، أو قل الكل للمسح الكامل"
        else:
            names_str = ", ".join(numbered_list) + ", or say all to delete everyone"
            
        self._say(_t("say_delete", names=names_str))
        
        matched = None
        for attempt in range(1, 4):
            target = self.stt.get_name(tries=2, timeout=10.0, tts=self.tts)
            if target:
                t_cleaned = target.lower().strip()
                if t_cleaned in ["cancel", "exit", "stop", "close", "الغي", "الغ", "الغاء", "إلغاء", "بلاش", "خروج", "اخرج"]:
                    self._say(_t("cancelled"))
                    return None
            if not target:
                if attempt < 3:
                    self._say(_t("try_again"))
                    continue
                else:
                    self._say(_t("no_name_heard"))
                    return None
            
            t_cleaned = _normalize_command_text(target)
            if _is_delete_all_command(target):
                if is_ar:
                    self._say("هل أنت متأكد تماماً من رغبتك في حذف جميع الأسماء المسجلة؟ قل نعم للتأكيد.")
                else:
                    self._say("Are you absolutely sure you want to delete all registered names? Say yes to confirm.")
                
                if self.stt.yes_no(tries=4, tts=self.tts) is not True:
                    self._say(_t("cancelled"))
                    return None
                    
                for name in ns:
                    self.db.delete(name)
                    
                if is_ar:
                    self._say("تم حذف جميع الأسماء بنجاح.")
                else:
                    self._say("All registered names have been successfully deleted.")
                return "deleted:__all__"
                
            num = _parse_number(target)
            if num is not None and 1 <= num <= len(ns):
                matched = ns[num - 1]
                break
            else:
                matched = next((n for n in ns if n.lower() == target.lower()
                                or target.lower() in n.lower()), None)
                if matched:
                    break
            
            self._say(_t("not_found", name=target))
            if attempt < 3:
                self._say(_t("try_again"))
                
        if not matched:
            return None
            
        self._say(_t("confirm_delete", name=matched))
        if self.stt.yes_no(tries=4, tts=self.tts) is not True:
            self._say(_t("cancelled"))
            return None
            
        self.db.delete(matched)
        self._say(_t("deleted", name=matched))
        return f"deleted:{matched}"

    # ── Block ─────────────────────────────────────────────────────────────────

    def _block(self):
        return self._do_block()

    def _do_block(self):
        self._say(_t("keep_person"))

        frame = None
        deadline = time.time() + 10.0
        while time.time() < deadline:
            try:
                frame = self._fq.get(timeout=1.0)
                break
            except queue.Empty:
                continue

        if frame is None:
            self._say(_t("no_frame"))
            return None

        faces = self.proc.detect(frame)
        if not faces:
            self._say(_t("no_face"))
            return None

        emb_check = self.proc.embed(frame, faces[0])
        if emb_check is not None:
            db = self.db.all()
            for name, rec in db.items():
                if name.startswith("__blocked__"): continue
                if not rec.embeddings: continue
                stored = np.array(rec.embeddings)
                dists  = 1.0 - (stored @ emb_check)
                top3   = sorted(dists)[:min(3, len(dists))]
                if float(np.mean(top3)) <= 0.45:
                    self._say(_t("already_reg", name=name))
                    return None

        self._say(_t("say_label"))
        label = self.stt.get_name(tries=3, timeout=10.0, tts=self.tts)
        if not label:
            self._say(_t("no_label"))
            return None

        self._say(_t("blocking", name=label))
        embs = self._capture_with_guidance()
        if len(embs) < 10:
            self._say(_t("not_enough"))
            return None

        block_id = f"__blocked__{label}"
        self.db.add(block_id, embs)
        self.blocked.add(block_id)
        save_blocked(self.blocked)
        self._say(_t("blocked", name=label))
        return f"blocked:{label}"

    # ── Unblock ───────────────────────────────────────────────────────────────

    def _unblock(self):
        blocked_names = [b.replace("__blocked__", "") for b in self.blocked]
        if not blocked_names:
            self._say(_t("no_blocked"))
            return None
        self._say(_t("say_unblock", names=", ".join(blocked_names)))
        
        matched_id = None
        for attempt in range(1, 4):
            target = self.stt.get_name(tries=2, timeout=10.0, tts=self.tts)
            if target:
                t_cleaned = target.lower().strip()
                if t_cleaned in ["cancel", "exit", "stop", "close", "الغي", "الغ", "الغاء", "إلغاء", "بلاش", "خروج", "اخرج"]:
                    self._say(_t("cancelled"))
                    return None
            if not target:
                if attempt < 3:
                    self._say(_t("try_again"))
                    continue
                else:
                    self._say(_t("no_name_heard"))
                    return None
            
            matched_id = next(
                (b for b in self.blocked if target.lower() in b.lower()), None)
            if matched_id:
                break
                
            self._say(_t("not_blocked", name=target))
            if attempt < 3:
                self._say(_t("try_again"))
                
        if not matched_id:
            return None
            
        target_name = matched_id.replace("__blocked__", "")
        self._say(_t("confirm_unblock", name=target_name))
        if self.stt.yes_no(tries=4, tts=self.tts) is not True:
            self._say(_t("cancelled"))
            return None
        self.blocked.discard(matched_id)
        self.db.delete(matched_id)
        save_blocked(self.blocked)
        self._say(_t("unblocked", name=target_name))
        return f"unblocked:{target_name}"

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _say(self, text: str):
        self.current_instruction = text
        self.tts.say_wait(text, pause=0.05)
